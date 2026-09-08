import hashlib
import json
import logging
import math
import sys
from pathlib import Path

from .media import probe, render, run
from .selection import transcript_chunks, request_candidates, rank
from .store import atomic_json

LOG = logging.getLogger("clipforge")


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def cached(path, signature):
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data["signature"] == signature:
                return data["value"]
        except (ValueError, KeyError, TypeError):
            pass
    return None


def do_transcribe(source, output, config, directory):
    runtime = directory / "runtime-config.json"
    # Configuration contains the environment-variable name, never the API key.
    atomic_json(runtime, config)
    run([sys.executable, "-m", "clipforge.transcribe", str(source), str(output), str(runtime)],
        config["transcription_timeout_seconds"])


def validate_transcript(transcript, duration):
    if not isinstance(transcript, dict) or not isinstance(transcript.get("segments"), list):
        raise ValueError("Invalid transcript structure")
    previous_start = -1
    for i, segment in enumerate(transcript["segments"]):
        start, end = segment["start"], segment["end"]
        if not all(type(v) in (int, float) and math.isfinite(v) for v in (start, end)):
            raise ValueError("Transcript has invalid timestamps")
        if not 0 <= start < end <= duration + 0.5 or start < previous_start:
            raise ValueError("Transcript timestamps fall outside the video or are unordered")
        segment["end"] = min(end, duration)
        segment["id"] = i
        previous_start = start
        if not isinstance(segment.get("text"), str):
            raise ValueError("Transcript segment text is missing")
        for word in segment.get("words", []):
            if not all(type(word.get(k)) in (int, float) and math.isfinite(word[k]) for k in ("start", "end")):
                raise ValueError("Transcript word has invalid timestamps")
            if word["end"] < word["start"] or not isinstance(word.get("text"), str):
                raise ValueError("Invalid transcript word")
    return transcript


def process(job, config, store):
    folder = Path(config["data_dir"]) / "jobs" / job["id"]
    source = folder / "source.video"
    details = probe(source, config)
    if not any(s["codec_type"] == "audio" for s in details["streams"]):
        raise ValueError("Video has no audio stream")
    if not any(s["codec_type"] == "video" for s in details["streams"]):
        raise ValueError("Source has no video stream")
    duration = float(details["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Source duration is invalid")
    transcript_signature = fingerprint({"source": job["id"], "version": 1,
        **{key: config[key] for key in ("whisper_model", "language", "whisper_compute_type")}})
    checkpoint = folder / "transcript-cache.json"
    transcript = cached(checkpoint, transcript_signature)
    if transcript is None:
        LOG.info("%s: transcribing", job["id"][:12])
        output = folder / "transcript.json"
        do_transcribe(source, output, config, folder)
        transcript = json.loads(output.read_text(encoding="utf-8"))
        validate_transcript(transcript, duration)
        atomic_json(checkpoint, {"signature": transcript_signature, "value": transcript})
    validate_transcript(transcript, duration)
    # Only text/timing enters the LLM; avoid wasting context on word-level captions.
    compact = [{k: s[k] for k in ("id", "start", "end", "text")} for s in transcript["segments"]]
    candidates = []
    selection_config = {k: v for k, v in config.items() if k.startswith("llm_") or k in (
        "min_clip_seconds", "max_clip_seconds", "min_score", "chunk_characters", "chunk_overlap_seconds")}
    for i, chunk in enumerate(transcript_chunks(compact, config["chunk_characters"], config["chunk_overlap_seconds"])):
        signature = fingerprint({"chunk": chunk, "config": selection_config, "prompt_version": 1})
        path = folder / "selection" / f"chunk-{i:04d}.json"
        found = cached(path, signature)
        if found is None:
            LOG.info("%s: selecting from transcript section %d", job["id"][:12], i + 1)
            found = request_candidates(chunk, config, store)
            atomic_json(path, {"signature": signature, "value": found})
        candidates.extend(found)
    clips = rank(candidates, config["clips_per_video"])
    atomic_json(folder / "selected-clips.json", clips)
    outputs = []
    for i, clip in enumerate(clips):
        render_config = {key: config[key] for key in ("width", "height", "fps", "font_name", "font_size", "caption_margin_bottom", "video_encoder")}
        signature = fingerprint({"clip": clip, "transcript": transcript_signature, "config": render_config, "renderer_version": 1})
        directory = folder / "outputs" / signature[:16]
        metadata = directory / "metadata.json"
        previous = cached(metadata, signature)
        file = directory / "clip.mp4"
        if previous is None or not file.is_file():
            LOG.info("%s: rendering clip %d/%d", job["id"][:12], i + 1, len(clips))
            file = Path(render(source, transcript, clip, directory, config))
            atomic_json(metadata, {"signature": signature, "value": clip})
        outputs.append({**clip, "file": str(file), "captions": str(directory / "captions.ass")})
    result = {"job_id": job["id"], "source_name": job["original_name"], "clips": outputs,
              "note": "No clips passed selection; nothing was rendered." if not clips else "Exported locally; no social publishing was performed."}
    atomic_json(folder / "result.json", result)
    return result
