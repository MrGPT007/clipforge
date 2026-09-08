import json
from copy import deepcopy
from pathlib import Path

DEFAULTS = {
    "data_dir": "data",
    "inbox_dir": "inbox",
    "scan_seconds": 15,
    "settle_seconds": 30,
    "max_attempts": 4,
    "retry_seconds": 60,
    "whisper_model": "small",
    "whisper_device": "cpu",
    "whisper_compute_type": "int8",
    "language": "en",
    "transcription_timeout_seconds": 14400,
    "llm_base_url": "http://127.0.0.1:1234/v1",
    "llm_model": "",
    "llm_api_key_env": "CLIPFORGE_API_KEY",
    "llm_response_format": "json_schema",
    "llm_timeout_seconds": 300,
    "llm_max_output_tokens": 1000,
    "llm_daily_request_limit": 30,
    "chunk_characters": 8000,
    "chunk_overlap_seconds": 45,
    "clips_per_video": 3,
    "min_clip_seconds": 15,
    "max_clip_seconds": 60,
    "min_score": 6,
    "width": 720,
    "height": 1280,
    "fps": 30,
    "font_name": "DejaVu Sans",
    "font_size": 42,
    "caption_margin_bottom": 160,
    "video_encoder": "libx264",
    "render_timeout_seconds": 3600,
    "ffmpeg": "ffmpeg",
    "ffprobe": "ffprobe"
}
DEFAULTS.update({
    "default_profile": "",
    "model_profiles": {},
    "download_timeout_seconds": 7200,
    "download_max_height": 1080,
    "download_max_bytes": 2147483648,
    "download_max_duration_seconds": 14400,
    "download_js_runtime": "deno"
})
PROFILE_KEYS = {k for k in DEFAULTS if k.startswith("llm_")} | {
    "whisper_model", "whisper_device", "whisper_compute_type", "language", "chunk_characters"
}


def for_profile(config, name=""):
    resolved = deepcopy(config)
    if name:
        if name not in config["model_profiles"]:
            raise ValueError(f"Unknown model profile: {name}")
        resolved.update(config["model_profiles"][name])
    for key in ("llm_timeout_seconds", "llm_max_output_tokens", "chunk_characters"):
        if type(resolved[key]) not in (int, float) or resolved[key] <= 0:
            raise ValueError(f"Invalid {key} in model profile")
    if type(resolved["llm_daily_request_limit"]) is not int or resolved["llm_daily_request_limit"] < 0:
        raise ValueError("llm_daily_request_limit must be a nonnegative integer")
    if resolved["llm_response_format"] not in ("json_schema", "json_object", "none"):
        raise ValueError("Invalid model response format")
    for key in ("llm_base_url", "llm_model", "llm_api_key_env", "whisper_model", "whisper_device", "whisper_compute_type"):
        if not isinstance(resolved[key], str):
            raise ValueError(f"{key} must be a string")
    return resolved


def load(path):
    path = Path(path).resolve()
    settings = deepcopy(DEFAULTS)
    overrides = json.loads(path.read_text(encoding="utf-8"))
    unknown = set(overrides) - set(settings)
    if unknown:
        raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
    settings.update(overrides)
    if not isinstance(settings["model_profiles"], dict):
        raise ValueError("model_profiles must be an object")
    for name, profile in settings["model_profiles"].items():
        if not name or not isinstance(profile, dict) or set(profile) - PROFILE_KEYS:
            raise ValueError(f"Invalid model profile: {name}")
    if settings["default_profile"] and settings["default_profile"] not in settings["model_profiles"]:
        raise ValueError("default_profile does not exist in model_profiles")
    for key in ("data_dir", "inbox_dir"):
        settings[key] = str((path.parent / settings[key]).resolve())
    for key in ("scan_seconds", "settle_seconds", "max_attempts", "retry_seconds",
                "chunk_characters", "clips_per_video", "min_clip_seconds",
                "max_clip_seconds", "width", "height", "fps", "font_size",
                "llm_timeout_seconds", "llm_max_output_tokens",
                "transcription_timeout_seconds", "render_timeout_seconds", "download_timeout_seconds",
                "download_max_height", "download_max_bytes", "download_max_duration_seconds"):
        if not isinstance(settings[key], (int, float)) or settings[key] <= 0:
            raise ValueError(f"{key} must be positive")
    if settings["chunk_characters"] < 500:
        raise ValueError("chunk_characters must be at least 500")
    if settings["min_clip_seconds"] > settings["max_clip_seconds"]:
        raise ValueError("min_clip_seconds must not exceed max_clip_seconds")
    if settings["width"] % 2 or settings["height"] % 2:
        raise ValueError("Video dimensions must be even integers")
    if settings["llm_response_format"] not in ("json_schema", "json_object", "none"):
        raise ValueError("Unsupported llm_response_format")
    if settings["video_encoder"] not in ("libx264", "h264_nvenc"):
        raise ValueError("video_encoder must be libx264 or h264_nvenc")
    if settings["download_js_runtime"] not in ("deno", "node", "quickjs", "bun", ""):
        raise ValueError("Unsupported download_js_runtime")
    return settings
