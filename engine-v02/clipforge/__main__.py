import argparse
import importlib.util
import json
import logging
import shutil
import sys
from pathlib import Path

from .config import DEFAULTS, load
from .service import serve
from .store import Store, atomic_json
from .control import execute


def main():
    parser = argparse.ArgumentParser(description="Portable automated clip production")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--profile", default=None, help="Named model profile for this command")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Create configuration and working folders")
    run = commands.add_parser("run", help="Run the internal scheduler and serial worker")
    run.add_argument("--once", action="store_true", help="Drain currently due jobs then exit; enqueue files first")
    add = commands.add_parser("enqueue", help="Queue a local video or a single video URL")
    add.add_argument("video")
    commands.add_parser("status", help="Return job status as JSON")
    retry = commands.add_parser("retry", help="Retry a failed or deferred job")
    retry.add_argument("job_id")
    commands.add_parser("doctor", help="Check local dependencies; does not contact any model")
    for command in ("start", "pause", "resume", "stop", "profiles", "models"):
        commands.add_parser(command)
    use_profile = commands.add_parser("use-profile", help="Choose the default profile for future intake")
    use_profile.add_argument("name")
    set_model = commands.add_parser("set-model", help="Select a model ID for the selected profile")
    set_model.add_argument("model_id")
    retry_download = commands.add_parser("retry-download")
    retry_download.add_argument("download_id")
    commands.add_parser("mcp", help="Run the optional stdio agent interface")
    commands.add_parser("add", help="Interactively paste a video URL or local path")
    args = parser.parse_args()
    config_path = Path(args.config)
    if args.command == "init":
        if config_path.exists():
            raise ValueError("Configuration already exists; edit it directly")
        atomic_json(config_path, DEFAULTS)
        config = load(config_path)
        for key in ("data_dir", "inbox_dir"):
            Path(config[key]).mkdir(parents=True, exist_ok=True)
        print(f"Created {config_path}. Set llm_model, then run doctor and run.")
        return
    config = load(config_path)
    if args.command == "mcp":
        from .mcp_server import serve_mcp
        serve_mcp(str(config_path.resolve()))
        return
    if args.command in ("start", "pause", "resume", "stop", "profiles", "models", "set-model", "status", "use-profile", "retry", "retry-download", "enqueue", "add"):
        action = args.command
        source = ""
        if action == "add":
            source = input("Paste a video URL or local video path: ").strip()
            if len(source) >= 2 and source[0] == source[-1] and source[0] in "\"'":
                source = source[1:-1]
            action = "submit"
        elif action == "enqueue":
            source = args.video
            action = "submit"
        selected = args.name if action == "use-profile" else args.profile
        identifier = getattr(args, "job_id", getattr(args, "download_id", getattr(args, "model_id", "")))
        print(json.dumps(execute(config_path, action, source=source, profile=selected, identifier=identifier), indent=2))
        return
    if args.command == "doctor":
        from .config import for_profile
        diagnostics_store = Store(config["data_dir"])
        try:
            profile = args.profile if args.profile is not None else diagnostics_store.get_control("active_profile", config["default_profile"])
            config = for_profile(config, profile)
            config["llm_model"] = diagnostics_store.get_control("model:" + profile, config["llm_model"])
        finally:
            diagnostics_store.close()
        ffmpeg_path = shutil.which(config["ffmpeg"])
        checks = {"python": sys.version.split()[0], "ffmpeg": ffmpeg_path,
                  "ffprobe": shutil.which(config["ffprobe"]),
                  "faster_whisper_installed": importlib.util.find_spec("faster_whisper") is not None,
                  "yt_dlp_installed": importlib.util.find_spec("yt_dlp") is not None,
                  "mcp_installed": importlib.util.find_spec("mcp") is not None,
                  "download_js_runtime": shutil.which(config["download_js_runtime"]) if config["download_js_runtime"] else None,
                  "model_configured": bool(config["llm_model"]),
                  "whisper_device": config["whisper_device"],
                  "note": "Does not verify model quality, GPU compatibility, or endpoint connectivity."}
        if ffmpeg_path:
            from .media import run as command_run
            checks["subtitle_filter_available"] = "subtitles" in command_run([ffmpeg_path, "-hide_banner", "-filters"], 30)
        print(json.dumps(checks, indent=2))
        return
    store = Store(config["data_dir"])
    try:
        if args.command == "run":
            if args.profile is not None:
                from .config import for_profile
                for_profile(config, args.profile)
                store.set_control("active_profile", args.profile)
            logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
            serve(config, store, args.once)
    finally:
        store.close()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError) as error:
        print(f"ClipForge: {error}", file=sys.stderr)
        sys.exit(1)
