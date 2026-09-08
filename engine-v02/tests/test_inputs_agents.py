import asyncio
import functools
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from clipforge.config import DEFAULTS, load, for_profile
from clipforge.control import execute
from clipforge.downloads import download_source, normalize_url
from clipforge.service import scan_urls, serve, Watcher
from clipforge.store import Store, atomic_json


class InputsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / "config.json"
        atomic_json(self.path, {"data_dir": "data", "inbox_dir": "inbox", "model_profiles": {
            "local": {"llm_model": "local-model"}, "cloud": {"llm_model": "cloud-model"}
        }})
        self.config = load(self.path)
        self.store = Store(self.config["data_dir"])

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_url_normalization_and_disallowed_schemes(self):
        self.assertEqual(normalize_url(" https://EXAMPLE.com/video.mp4#fragment "), "https://example.com/video.mp4")
        for url in ("file:///secret", "ftp://example.com/video", "https://user:password@example.com/x", "--exec malicious"):
            with self.assertRaises(ValueError): normalize_url(url)

    def test_urls_persist_dedupe_and_recover(self):
        a = self.store.queue_url("https://example.com/video.mp4", "local")
        self.assertEqual(a, self.store.queue_url("https://example.com/video.mp4#x", "local"))
        self.store.claim_download()
        self.store.recover()
        self.assertEqual(self.store.claim_download()["id"], a)
        self.assertNotEqual(a, self.store.queue_url("https://example.com/video.mp4", "cloud"))

    def test_url_intake_is_not_replayed_when_model_changes(self):
        folder = Path(self.config["inbox_dir"])
        folder.mkdir()
        (folder / "urls.txt").write_text("# videos\nhttps://example.com/video.mp4\n", encoding="utf-8")
        scan_urls(folder, self.store, "local")
        scan_urls(folder, self.store, "cloud")
        self.assertEqual(len(self.store.downloads()), 1)
        self.assertEqual(self.store.downloads()[0]["profile"], "local")

    def test_local_intake_survives_restart_without_replay(self):
        folder = Path(self.config["inbox_dir"])
        watcher = Watcher(folder, 1)
        (folder / "input.mp4").write_bytes(b"video-bytes")
        watcher.scan(self.store, now=0, profile="local")
        watcher.scan(self.store, now=2, profile="local")
        after_restart = Watcher(folder, 1)
        after_restart.scan(self.store, now=4, profile="cloud")
        after_restart.scan(self.store, now=6, profile="cloud")
        self.assertEqual(len(self.store.jobs()), 1)

    def test_profiles_bind_at_submission_and_reject_unknown(self):
        execute(self.path, "use-profile", profile="local")
        result = execute(self.path, "submit", source="https://example.com/video.mp4")
        execute(self.path, "use-profile", profile="cloud")
        self.assertEqual(self.store.downloads()[0]["profile"], "local")
        self.assertEqual(for_profile(self.config, "cloud")["llm_model"], "cloud-model")
        with self.assertRaises(ValueError): execute(self.path, "submit", source="https://example.com/x", profile="missing")

    def test_pause_and_resume(self):
        execute(self.path, "pause")
        serve(self.config, self.store, once=True)
        self.assertTrue(execute(self.path, "status")["paused"])
        execute(self.path, "resume")
        self.assertFalse(execute(self.path, "status")["paused"])

    def test_model_choice_persists_without_rewriting_config(self):
        before = self.path.read_text()
        execute(self.path, "set-model", profile="local", identifier="another-local-model")
        profiles = execute(self.path, "profiles")
        self.assertEqual(profiles["profiles"]["local"]["llm_model"], "another-local-model")
        self.assertEqual(self.path.read_text(), before)
        with self.assertRaises(ValueError):
            execute(self.path, "set-model", profile="local", identifier="")

    def test_download_retry_is_bounded(self):
        self.store.queue_url("https://example.com/video.mp4")
        download = self.store.claim_download()
        self.store.fail_download(download, "offline", {**self.config, "max_attempts": 1})
        self.assertEqual(self.store.downloads()[0]["state"], "failed")
        self.assertIsNone(self.store.claim_download())
        self.store.retry_download(download["id"])
        self.assertIsNotNone(self.store.claim_download())


@unittest.skipUnless(importlib.util.find_spec("yt_dlp") and shutil.which("ffmpeg"), "yt-dlp and FFmpeg required")
class RealDownloadTests(unittest.TestCase):
    def test_real_http_download_enters_editing_queue_and_reuses_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.mp4"
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:s=160x90:r=10", "-f", "lavfi", "-i", "sine=frequency=440", "-t", "2", "-c:v", "libx264", "-threads", "2", "-c:a", "aac", str(source)], check=True, timeout=30)
            class QuietHandler(SimpleHTTPRequestHandler):
                def log_message(self, *_): pass
            server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(root)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            config = {**DEFAULTS, "data_dir": str(root / "data"), "inbox_dir": str(root / "inbox"), "download_js_runtime": ""}
            store = Store(config["data_dir"])
            try:
                identifier = store.queue_url(f"http://127.0.0.1:{server.server_port}/source.mp4")
                download = store.claim_download()
                job_id = download_source(download, config, store)
                self.assertEqual(store.downloads()[0]["job_id"], job_id)
                self.assertEqual(store.downloads()[0]["state"], "done")
                with patch("clipforge.downloads.run", side_effect=AssertionError("download repeated")):
                    self.assertEqual(download_source(download, config, store), job_id)
                self.assertEqual(len(store.jobs()), 1)
                self.assertEqual(store.claim()["id"], job_id)
            finally:
                store.close()
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


@unittest.skipUnless(importlib.util.find_spec("mcp"), "MCP optional dependency required")
class MCPTests(unittest.TestCase):
    def test_actual_stdio_handshake_tool_discovery_and_url_submission(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        with tempfile.TemporaryDirectory() as temp:
            config_path = Path(temp) / "config.json"
            atomic_json(config_path, {"data_dir": "data", "inbox_dir": "inbox"})
            async def check():
                params = StdioServerParameters(command=sys.executable, args=["-m", "clipforge", "--config", str(config_path), "mcp"], env=dict(os.environ))
                async with stdio_client(params) as (reader, writer):
                    async with ClientSession(reader, writer) as session:
                        await session.initialize()
                        listing = await session.list_tools()
                        self.assertIn("submit_video", {tool.name for tool in listing.tools})
                        response = await session.call_tool("submit_video", {"source": "https://example.com/video.mp4"})
                        self.assertFalse(response.isError)
                        response = await session.call_tool("processing_status", {})
                        self.assertFalse(response.isError)
            asyncio.run(check())
            store = Store(Path(temp) / "data")
            try:
                self.assertEqual(len(store.downloads()), 1)
            finally:
                store.close()


if __name__ == "__main__": unittest.main()
