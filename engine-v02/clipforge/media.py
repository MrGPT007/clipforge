import json
import math
import os
import subprocess
from pathlib import Path


def run(command, timeout, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=timeout, check=False)
    except FileNotFoundError:
        raise RuntimeError(f"Required executable not found: {command[0]}") from None
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Processing exceeded timeout ({timeout} seconds)") from None
    if result.returncode:
        raise RuntimeError(result.stderr[-1800:] or f"Command exited with status {result.returncode}")
    return result.stdout


def probe(path, config):
    return json.loads(run([config["ffprobe"], "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)], 30))


def timestamp(seconds):
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole_seconds, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{fraction:02d}"


def safe_text(text):
    # Prevent transcript text from becoming subtitle override tags or line escapes.
    return text.replace("\\", "/").replace("{", "(").replace("}", ")").replace("\n", " ").replace("\r", " ")


def captions(segments, start, end, config):
    font = config["font_name"].replace(",", " ").replace("\n", " ")
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {config['width']}
PlayResY: {config['height']}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{config['font_size']},&H0000FFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,50,50,{config['caption_margin_bottom']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for segment in segments:
        if segment["end"] <= start or segment["start"] >= end:
            continue
        words = [w for w in segment.get("words", []) if w["end"] > start and w["start"] < end]
        if not words:
            lines.append(f"Dialogue: 0,{timestamp(max(start, segment['start']) - start)},{timestamp(min(end, segment['end']) - start)},Default,,0,0,0,,{safe_text(segment['text'])}")
            continue
        # Short groups avoid unreadable walls of subtitles; \k uses ASR word timing.
        groups, group = [], []
        for word in words:
            if group and (len(group) >= 5 or sum(len(w['text']) + 1 for w in group) + len(word['text']) > 32):
                groups.append(group)
                group = []
            group.append(word)
        if group:
            groups.append(group)
        for group in groups:
            a = max(start, group[0]["start"])
            b = min(end, group[-1]["end"])
            if b <= a:
                continue
            parts = []
            for i, word in enumerate(group):
                next_time = group[i + 1]["start"] if i + 1 < len(group) else b
                duration = max(1, round((min(b, next_time) - max(a, word["start"])) * 100))
                parts.append("{\\k" + str(duration) + "}" + safe_text(word["text"]))
            lines.append(f"Dialogue: 0,{timestamp(a-start)},{timestamp(b-start)},Default,,0,0,0,,{' '.join(parts)}")
    return header + "\n".join(lines) + "\n"


def render(source, transcript, clip, directory, config):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / "clip.mp4"
    temporary = directory / "clip.partial.mp4"
    subtitle = directory / "captions.ass"
    subtitle.write_text(captions(transcript["segments"], clip["start"], clip["end"], config), encoding="utf-8")
    w, h = config["width"], config["height"]
    # Fit foreground without cutting faces; background fills the vertical canvas.
    # Fixed local subtitle filename avoids Windows drive-letter/filter escaping bugs.
    filters = (
        f"[0:v]split=2[bg][fg];"
        f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=12:1[back];"
        f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2[front];"
        "[back][front]overlay=(W-w)/2:(H-h)/2,setsar=1,subtitles=captions.ass[v]"
    )
    command = [config["ffmpeg"], "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
               "-ss", str(clip["start"]), "-i", str(Path(source).resolve()),
               "-t", str(clip["end"] - clip["start"]), "-filter_complex_threads", "1",
               "-filter_complex", filters, "-map", "[v]", "-map", "0:a:0",
               "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-r", str(config["fps"]),
               "-c:v", config["video_encoder"], "-pix_fmt", "yuv420p", "-threads", "4"]
    command += ["-preset", "veryfast", "-crf", "22"] if config["video_encoder"] == "libx264" else ["-preset", "p4", "-cq", "23"]
    command += ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(temporary)]
    try:
        run(command, config["render_timeout_seconds"], cwd=directory)
        details = probe(temporary, config)
        duration = float(details["format"]["duration"])
        expected = clip["end"] - clip["start"]
        videos = [s for s in details["streams"] if s["codec_type"] == "video"]
        if not videos or (videos[0]["width"], videos[0]["height"]) != (w, h):
            raise RuntimeError("Rendered clip has incorrect dimensions")
        if not math.isfinite(duration) or abs(duration - expected) > 1:
            raise RuntimeError("Rendered duration failed validation")
        if not any(s["codec_type"] == "audio" for s in details["streams"]):
            raise RuntimeError("Rendered clip has no audio stream")
        os.replace(temporary, output)
        return str(output)
    finally:
        temporary.unlink(missing_ok=True)
