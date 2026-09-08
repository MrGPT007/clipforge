"""Run in a separate process so model memory is released on completion."""
import json
import sys
from pathlib import Path

from .store import atomic_json


def transcribe(source, output, config):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError("Install the speech extra: python -m pip install -e '.[speech]'") from None
    model = WhisperModel(config["whisper_model"], device=config["whisper_device"],
                         compute_type=config["whisper_compute_type"],
                         download_root=str(Path(config["data_dir"]) / "models"), cpu_threads=4)
    stream, info = model.transcribe(str(source), language=config["language"] or None,
                                   word_timestamps=True, vad_filter=True, beam_size=5)
    segments = []
    for segment in stream:
        if not segment.text.strip():
            continue
        segments.append({"id": len(segments), "start": float(segment.start), "end": float(segment.end),
                         "text": segment.text.strip(),
                         "words": [{"start": float(w.start), "end": float(w.end), "text": w.word.strip()}
                                   for w in (segment.words or []) if w.word.strip()]})
    atomic_json(output, {"language": info.language, "duration": info.duration, "segments": segments})


if __name__ == "__main__":
    try:
        transcribe(Path(sys.argv[1]), Path(sys.argv[2]), json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")))
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
