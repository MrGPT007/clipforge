"""Isolated yt-dlp execution, bounded by the parent process timeout."""
import json
import sys
from pathlib import Path

from .downloads import normalize_url
from .store import atomic_json, VIDEO_EXTENSIONS


class QuietLogger:
    def debug(self, message): pass
    def warning(self, message): pass
    def error(self, message): pass


def fetch(url, folder, config):
    try:
        from yt_dlp import YoutubeDL
    except ImportError:
        raise RuntimeError("Install the downloads extra") from None
    url = normalize_url(url)
    folder = Path(folder).resolve()
    limit = config["download_max_bytes"]

    def progress(event):
        if event.get("downloaded_bytes", 0) > limit:
            raise RuntimeError("Download size limit exceeded")

    options = {
        "outtmpl": str(folder / "source.%(ext)s"), "noplaylist": True,
        "lazy_playlist": True, "playlistend": 1,
        "format": f"bv*[height<=?{config['download_max_height']}]+ba/b[height<=?{config['download_max_height']}]",
        "merge_output_format": "mkv", "max_filesize": limit,
        "socket_timeout": 30, "retries": 2, "fragment_retries": 2,
        "concurrent_fragment_downloads": 1, "quiet": True,
        "logger": QuietLogger(), "progress_hooks": [progress], "continuedl": True,
        "ffmpeg_location": config["ffmpeg"], "cachedir": str(folder / "extractor-cache")
    }
    if config["download_js_runtime"]:
        options["js_runtimes"] = {config["download_js_runtime"]: {}}
    with YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=False)
        if not info or info.get("_type") in ("playlist", "multi_video") or "entries" in info:
            raise ValueError("Use a single video URL, not a channel or playlist")
        if info.get("is_live") or info.get("live_status") in ("is_live", "is_upcoming"):
            raise ValueError("Live and upcoming streams are not supported")
        if info.get("duration") and info["duration"] > config["download_max_duration_seconds"]:
            raise ValueError("Video duration exceeds configured limit")
        downloader.process_info(info)
    candidates = [p for p in folder.glob("source.*") if p.suffix.lower() in VIDEO_EXTENSIONS and p.is_file()]
    if len(candidates) != 1:
        raise RuntimeError("Downloader did not produce one complete supported video")
    source = candidates[0]
    if source.stat().st_size > limit:
        source.unlink()
        raise RuntimeError("Completed download exceeds configured size limit")
    atomic_json(folder / "download.json", {"filename": source.name})


if __name__ == "__main__":
    try:
        fetch(sys.argv[1], sys.argv[2], json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")))
    except Exception:
        print("Download failed; verify dependencies, URL access and configured limits.", file=sys.stderr)
        sys.exit(1)
