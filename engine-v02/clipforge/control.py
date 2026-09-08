"""Shared command surface for CLI and MCP; no arbitrary shell execution."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

from .config import load, for_profile
from .store import Store, worker_lock


def running(data_dir):
    try:
        with worker_lock(data_dir):
            return False
    except RuntimeError:
        return True


def execute(config_path, action, source="", profile=None, identifier=""):
    config_path = str(Path(config_path).resolve())
    config = load(config_path)
    store = Store(config["data_dir"])
    try:
        selected = profile if profile is not None else store.get_control("active_profile", config["default_profile"])
        selected_config = for_profile(config, selected)
        override = store.get_control("model:" + selected)
        if override:
            selected_config["llm_model"] = override
        if action == "submit":
            if source.strip().lower().startswith(("http://", "https://")):
                return {"download_id": store.queue_url(source, selected), "profile": selected}
            return {"job_id": store.enqueue(source, selected), "profile": selected}
        if action == "status":
            return {"worker_running": running(config["data_dir"]), "paused": store.get_control("paused") == "true",
                    "active_profile": selected, "jobs": store.jobs(), "downloads": store.downloads()}
        if action == "profiles":
            profiles = {}
            for name in ["", *config["model_profiles"]]:
                settings = for_profile(config, name)
                profiles[name] = {"llm_model": store.get_control("model:" + name, settings["llm_model"]),
                                  "llm_base_url": settings["llm_base_url"], "whisper_model": settings["whisper_model"]}
            return {"active_profile": selected, "profiles": profiles}
        if action == "set-model":
            if not identifier.strip() or len(identifier) > 512 or any(ord(c) < 32 for c in identifier):
                raise ValueError("Provide a valid model ID from the endpoint")
            store.set_control("model:" + selected, identifier.strip())
            return {"profile": selected, "llm_model": identifier.strip(), "note": "Applies when jobs for this profile next begin processing; endpoint availability is not verified."}
        if action == "use-profile":
            if profile is None:
                raise ValueError("Specify a profile, or an empty string for base settings")
            store.set_control("active_profile", selected)
            return {"active_profile": selected, "note": "Applies to future submissions; queued jobs retain their profile."}
        if action == "models":
            headers = {}
            key = os.environ.get(selected_config["llm_api_key_env"])
            if key:
                headers["Authorization"] = "Bearer " + key
            try:
                with urlopen(Request(selected_config["llm_base_url"].rstrip("/") + "/models", headers=headers), timeout=30) as response:
                    value = json.load(response)
                return {"profile": selected, "models": [row["id"] for row in value["data"]]}
            except Exception:
                raise RuntimeError("Unable to list models; verify endpoint, credentials and /models support") from None
        if action in ("pause", "resume", "stop"):
            store.set_control("stop_requested" if action == "stop" else "paused", "false" if action == "resume" else "true")
            return {"action": action, "note": "Takes effect between processing stages/jobs; active subprocesses are not killed."}
        if action == "retry":
            store.retry(identifier)
            return {"job_queued": identifier}
        if action == "retry-download":
            store.retry_download(identifier)
            return {"download_queued": identifier}
        if action == "start":
            if running(config["data_dir"]):
                return {"worker_running": True, "already_running": True}
            log_path = Path(config["data_dir"]) / "worker.log"
            with log_path.open("ab") as log:
                child = subprocess.Popen([sys.executable, "-m", "clipforge", "--config", config_path, "run"],
                                         stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
            for _ in range(20):
                if running(config["data_dir"]):
                    return {"worker_running": True, "pid": child.pid, "log": str(log_path)}
                if child.poll() is not None:
                    raise RuntimeError("Worker exited during startup; inspect data/worker.log")
                time.sleep(0.1)
            return {"worker_starting": True, "pid": child.pid, "log": str(log_path)}
        raise ValueError("Unknown control action")
    finally:
        store.close()
