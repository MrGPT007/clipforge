import logging
import hashlib
import json
import signal
import threading
import time
from pathlib import Path

from .pipeline import process
from .config import for_profile
from .downloads import download_source
from .store import DailyLimit, VIDEO_EXTENSIONS, worker_lock

LOG = logging.getLogger("clipforge")


class Watcher:
    def __init__(self, folder, settle_seconds):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.settle_seconds = settle_seconds
        self.observed = {}
        self.submitted = {}

    def scan(self, store, now=None, profile=""):
        now = time.monotonic() if now is None else now
        present = set()
        for path in self.folder.iterdir():
            if path.suffix.lower() not in VIDEO_EXTENSIONS or not path.is_file():
                continue
            present.add(path)
            try:
                stat = path.stat()
                signature = (stat.st_size, stat.st_mtime_ns)
                persistent_key = "inbox:" + hashlib.sha256(str(path.resolve()).encode()).hexdigest()
                if store.get_control(persistent_key) == json.dumps(signature):
                    continue
                if self.submitted.get(path) == signature:
                    continue
                previous = self.observed.get(path)
                if previous is None or previous[0] != signature:
                    self.observed[path] = (signature, now)
                    continue
                if now - previous[1] >= self.settle_seconds:
                    job_id = store.enqueue(path, profile)
                    self.submitted[path] = signature
                    store.set_control(persistent_key, json.dumps(signature))
                    LOG.info("Queued %s as %s", path.name, job_id[:12])
            except (OSError, ValueError) as error:
                LOG.warning("Inbox file not ready: %s", error)
        for path in set(self.observed) - present:
            self.observed.pop(path, None)
            self.submitted.pop(path, None)


def scan_urls(folder, store, profile):
    path = Path(folder) / "urls.txt"
    if not path.is_file():
        return
    # Read a bounded UTF-8 file, retaining successful URLs in the persistent queue.
    if path.stat().st_size > 1024 * 1024:
        LOG.warning("urls.txt exceeds 1 MiB; split the intake into smaller batches")
        return
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        LOG.warning("Could not read urls.txt as UTF-8")
        return
    for line_number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            from .downloads import normalize_url
            normalized = normalize_url(line)
            key = "url-intake:" + hashlib.sha256(normalized.encode()).hexdigest()
            if not store.get_control(key):
                identifier = store.queue_url(normalized, profile)
                store.set_control(key, identifier)
        except ValueError:
            LOG.warning("Invalid URL on urls.txt line %d", line_number)


def serve(config, store, once=False):
    stop = threading.Event()
    old_handlers = {}
    if threading.current_thread() is threading.main_thread():
        for event in (signal.SIGTERM, signal.SIGINT):
            old_handlers[event] = signal.signal(event, lambda *_: stop.set())
    try:
        with worker_lock(config["data_dir"]):
            store.recover()
            store.set_control("stop_requested", "false")
            watcher = Watcher(config["inbox_dir"], config["settle_seconds"])
            LOG.info("Worker running; watching %s", config["inbox_dir"])
            while not stop.is_set():
                if store.get_control("stop_requested") == "true":
                    break
                if store.get_control("paused") == "true":
                    if once:
                        break
                    stop.wait(config["scan_seconds"])
                    continue
                profile = store.get_control("active_profile", config["default_profile"])
                watcher.scan(store, profile=profile)
                scan_urls(config["inbox_dir"], store, profile)
                download = store.claim_download()
                if download:
                    try:
                        download_source(download, config, store)
                    except Exception:
                        store.fail_download(download, "Download failed; check URL access, dependencies and configured limits", config)
                        LOG.warning("Download %s failed; see downloads status", download["id"][:12])
                if stop.is_set() or store.get_control("stop_requested") == "true":
                    break
                if store.get_control("paused") == "true":
                    if once:
                        break
                    continue
                job = store.claim()
                if job:
                    job_config = config
                    try:
                        job_config = for_profile(config, job.get("profile", ""))
                        model_override = store.get_control("model:" + job.get("profile", ""))
                        if model_override:
                            job_config["llm_model"] = model_override
                        store.finish(job["id"], process(job, job_config, store))
                        LOG.info("%s: complete", job["id"][:12])
                    except DailyLimit:
                        store.defer_quota(job["id"])
                        LOG.warning("AI request cap reached; job deferred until next UTC day")
                    except Exception as error:
                        # Redact configured credentials even if a dependency echoed them.
                        import os
                        message = str(error)
                        secret = os.environ.get(job_config["llm_api_key_env"])
                        if secret:
                            message = message.replace(secret, "[redacted]")
                        store.fail(job, message, config)
                        LOG.error("%s: %s", job["id"][:12], message)
                elif once and not download:
                    break
                else:
                    stop.wait(config["scan_seconds"])
    finally:
        for event, previous in old_handlers.items():
            signal.signal(event, previous)
