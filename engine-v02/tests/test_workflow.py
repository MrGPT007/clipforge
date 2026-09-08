import json
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from clipforge.config import DEFAULTS, load
from clipforge.media import captions, probe
from clipforge.pipeline import process
from clipforge.selection import validate_candidates, rank, transcript_chunks
from clipforge.service import Watcher, serve
from clipforge.store import DailyLimit, Store, atomic_json, worker_lock


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / "data")
        self.config = {**DEFAULTS, "data_dir": str(self.root / "data"), "inbox_dir": str(self.root / "inbox")}

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def video(self, name="sample.mp4"):
        path = self.root / name
        path.write_bytes(b"test-source-bytes")
        return path

    def test_duplicate_content_is_one_job_and_original_preserved(self):
        first = self.video()
        second = self.video("renamed.mov")
        self.assertEqual(self.store.enqueue(first), self.store.enqueue(second))
        self.assertEqual(len(self.store.jobs()), 1)
        self.assertEqual(first.read_bytes(), b"test-source-bytes")

    def test_crash_recovery_and_single_worker_lock(self):
        job_id = self.store.enqueue(self.video())
        self.store.claim()
        with worker_lock(self.store.root):
            with self.assertRaises(RuntimeError):
                with worker_lock(self.store.root):
                    pass
        with worker_lock(self.store.root):
            self.store.recover()
            self.assertEqual(self.store.claim()["id"], job_id)

    def test_retry_is_bounded_and_not_claimed_early(self):
        self.store.enqueue(self.video())
        job = self.store.claim()
        self.store.fail(job, "offline", self.config)
        self.assertIsNone(self.store.claim())
        self.store.retry(job["id"])
        job = self.store.claim()
        self.store.fail(job, "offline", {**self.config, "max_attempts": 1})
        self.assertEqual(self.store.jobs()[0]["state"], "failed")

    def test_quota_persists_and_defers_without_consuming_attempt(self):
        self.store.reserve_request(1)
        another = Store(self.store.root)
        try:
            with self.assertRaises(DailyLimit):
                another.reserve_request(1)
        finally:
            another.close()
        job_id = self.store.enqueue(self.video())
        self.store.claim()
        self.store.defer_quota(job_id)
        row = self.store.jobs()[0]
        self.assertEqual(row["attempts"], 0)
        self.assertGreater(row["next_run"], time.time())

    def test_watcher_waits_for_complete_file(self):
        watcher = Watcher(self.config["inbox_dir"], 30)
        file = Path(self.config["inbox_dir"]) / "incoming.mp4"
        file.write_bytes(b"part")
        watcher.scan(self.store, now=0)
        watcher.scan(self.store, now=29)
        self.assertEqual(self.store.jobs(), [])
        file.write_bytes(b"complete")
        watcher.scan(self.store, now=30)
        watcher.scan(self.store, now=59)
        self.assertEqual(self.store.jobs(), [])
        watcher.scan(self.store, now=61)
        watcher.scan(self.store, now=90)
        self.assertEqual(len(self.store.jobs()), 1)

    def test_service_failure_is_recorded_and_secret_redacted(self):
        self.store.enqueue(self.video())
        with patch.dict("os.environ", {"CLIPFORGE_API_KEY": "secret-example"}), patch("clipforge.service.process", side_effect=RuntimeError("failure secret-example")):
            serve(self.config, self.store, once=True)
        row = self.store.jobs()[0]
        self.assertEqual(row["state"], "retry")
        self.assertNotIn("secret-example", row["error"])


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.segments = [{"id": i, "start": i * 10, "end": (i + 1) * 10, "text": "Example."} for i in range(10)]

    def test_hallucinated_ids_rejected(self):
        item = {"first_segment": 0, "last_segment": 999, "score": 8, "title": "x", "reason": "x"}
        with self.assertRaises(ValueError):
            validate_candidates({"clips": [item]}, self.segments, DEFAULTS)

    def test_nonfinite_score_rejected(self):
        item = {"first_segment": 0, "last_segment": 2, "score": float("nan"), "title": "x", "reason": "x"}
        with self.assertRaises(ValueError):
            validate_candidates({"clips": [item]}, self.segments, DEFAULTS)

    def test_duration_and_overlap_constraints(self):
        item = {"first_segment": 0, "last_segment": 9, "score": 8, "title": "x", "reason": "x"}
        self.assertEqual(validate_candidates({"clips": [item]}, self.segments, DEFAULTS), [])
        selected = rank([{"start": 0, "end": 30, "score": 8}, {"start": 10, "end": 40, "score": 9}, {"start": 40, "end": 60, "score": 7}], 3)
        self.assertEqual([s["start"] for s in selected], [10, 40])

    def test_chunking_covers_entire_transcript(self):
        chunks = list(transcript_chunks(self.segments, 300, 10))
        self.assertEqual({s["id"] for chunk in chunks for s in chunk}, set(range(10)))
        self.assertGreater(len(chunks), 1)

    def test_caption_override_text_is_escaped(self):
        text = captions([{"start": 0, "end": 2, "text": "{\\pos(0,0)} hello", "words": []}], 0, 2, DEFAULTS)
        self.assertNotIn("{\\pos", text)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class RenderIntegrationTest(unittest.TestCase):
    def test_real_render_http_selection_and_checkpoint_reuse(self):
        requests = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                requests.append(payload)
                response = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"clips": [
                    {"first_segment": 1, "last_segment": 3, "title": "A complete moment", "reason": "A hook and payoff", "score": 8}
                ]})}}]}
                encoded = json.dumps(response).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                source = root / "input with spaces.mp4"
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", "8", "-c:v", "libx264", "-threads", "2", "-c:a", "aac", str(source)], check=True, timeout=30)
                config = {**DEFAULTS, "data_dir": str(root / "data"), "width": 360, "height": 640,
                          "font_size": 24, "caption_margin_bottom": 80, "min_clip_seconds": 1, "max_clip_seconds": 10,
                          "llm_model": "test-model", "llm_base_url": f"http://127.0.0.1:{server.server_port}/v1"}
                transcript = {"language": "en", "duration": 8, "segments": [
                    {"id": i, "start": i * 2, "end": (i + 1) * 2, "text": f"Caption number {i}", "words": [
                        {"start": i*2, "end": i*2+0.6, "text": "Caption"},
                        {"start": i*2+0.6, "end": i*2+1.3, "text": "number"},
                        {"start": i*2+1.3, "end": (i+1)*2, "text": str(i)}]}
                    for i in range(4)]}
                store = Store(config["data_dir"])
                try:
                    store.enqueue(source)
                    job = store.claim()
                    def fake_transcribe(source, output, config, directory):
                        atomic_json(output, transcript)
                    with patch("clipforge.pipeline.do_transcribe", side_effect=fake_transcribe) as transcription:
                        result = process(job, config, store)
                        first_file = Path(result["clips"][0]["file"])
                        first_mtime = first_file.stat().st_mtime_ns
                        again = process(job, config, store)
                        self.assertEqual(transcription.call_count, 1)
                    self.assertEqual(len(requests), 1)
                    self.assertEqual(requests[0]["response_format"]["type"], "json_schema")
                    self.assertEqual(first_file.stat().st_mtime_ns, first_mtime)
                    self.assertEqual(again, result)
                    details = probe(first_file, config)
                    video = next(s for s in details["streams"] if s["codec_type"] == "video")
                    self.assertEqual((video["width"], video["height"]), (360, 640))
                    self.assertAlmostEqual(float(details["format"]["duration"]), 6, delta=0.2)
                    self.assertTrue(any(s["codec_type"] == "audio" for s in details["streams"]))
                finally:
                    store.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
