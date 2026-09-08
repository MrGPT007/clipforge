import json
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .media import probe, run
from .store import atomic_json, VIDEO_EXTENSIONS


def normalize_url(value):
    value = value.strip()
    if len(value) > 8192 or any(ord(c) < 32 for c in value):
        raise ValueError("Invalid video URL")
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
        raise ValueError("Use an http:// or https:// video URL")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing embedded credentials are not supported")
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.query, ""))


def download_source(item, config, store):
    folder = Path(config["data_dir"]) / "downloads" / item["id"]
    folder.mkdir(parents=True, exist_ok=True)
    manifest = folder / "download.json"
    if not manifest.exists():
        runtime = folder / "runtime-config.json"
        atomic_json(runtime, config)
        try:
            run([sys.executable, "-m", "clipforge.download_task", item["url"], str(folder), str(runtime)], config["download_timeout_seconds"])
        except RuntimeError:
            # Extractor logs can contain signed URLs/cookies: keep errors generic here.
            raise RuntimeError("Download failed or timed out. Check URL access, yt-dlp/JS-runtime installation, format support and configured limits.") from None
    value = json.loads(manifest.read_text(encoding="utf-8"))
    source = (folder / value["filename"]).resolve()
    if source.parent != folder.resolve() or source.suffix.lower() not in VIDEO_EXTENSIONS or not source.is_file():
        manifest.unlink(missing_ok=True)
        raise ValueError("Download checkpoint is invalid; retry to download again")
    details = probe(source, config)
    if not any(s["codec_type"] == "video" for s in details["streams"]):
        raise ValueError("Downloaded content is not a video")
    if float(details["format"]["duration"]) > config["download_max_duration_seconds"]:
        raise ValueError("Downloaded video exceeds the duration limit")
    job_id = store.enqueue(source, item["profile"])
    store.finish_download(item["id"], job_id)
    return job_id
