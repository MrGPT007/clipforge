import hashlib
import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".webm", ".m4v"}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def worker_lock(data_dir):
    """A process-held SQLite lock; released by the runtime even after a crash."""
    connection = sqlite3.connect(Path(data_dir) / "worker-lock.sqlite3", timeout=0)
    try:
        try:
            connection.execute("BEGIN EXCLUSIVE")
        except sqlite3.OperationalError as exc:
            raise RuntimeError("Another ClipForge worker already owns this data directory") from exc
        yield
    finally:
        connection.close()


class DailyLimit(Exception):
    pass


class Store:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / "queue.sqlite3", timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, original_name TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0,
                next_run REAL NOT NULL DEFAULT 0, created REAL NOT NULL, updated REAL NOT NULL,
                error TEXT, result TEXT
            );
            CREATE TABLE IF NOT EXISTS requests (
                day TEXT PRIMARY KEY, count INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS downloads (
                id TEXT PRIMARY KEY, url TEXT NOT NULL, profile TEXT NOT NULL DEFAULT '',
                state TEXT NOT NULL DEFAULT 'queued', attempts INTEGER NOT NULL DEFAULT 0,
                next_run REAL NOT NULL DEFAULT 0, created REAL NOT NULL, updated REAL NOT NULL,
                error TEXT, job_id TEXT
            );
            CREATE TABLE IF NOT EXISTS controls (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        if "profile" not in {r["name"] for r in self.db.execute("PRAGMA table_info(jobs)")}:
            try:
                self.db.execute("ALTER TABLE jobs ADD COLUMN profile TEXT NOT NULL DEFAULT ''")
                self.db.commit()
            except sqlite3.OperationalError:
                if "profile" not in {r["name"] for r in self.db.execute("PRAGMA table_info(jobs)")}:
                    raise

    def close(self):
        self.db.close()

    def enqueue(self, source, profile=""):
        source = Path(source).resolve()
        if source.suffix.lower() not in VIDEO_EXTENSIONS or not source.is_file():
            raise ValueError("Source must be an existing supported video file")
        before = source.stat()
        digest = hashlib.sha256()
        staging = self.root / ("staging-" + uuid.uuid4().hex)
        try:
            with source.open("rb") as incoming, staging.open("wb") as outgoing:
                while block := incoming.read(1024 * 1024):
                    digest.update(block)
                    outgoing.write(block)
            after = source.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError("Source changed while copying; will retry after it settles")
            job_id = digest.hexdigest()
            if profile:
                job_id = hashlib.sha256((job_id + "\0" + profile).encode()).hexdigest()
            folder = self.root / "jobs" / job_id
            folder.mkdir(parents=True, exist_ok=True)
            with self.db:
                self.db.execute("BEGIN IMMEDIATE")
                existing = self.db.execute("SELECT id FROM jobs WHERE id=?", (job_id,)).fetchone()
                if not existing:
                    # Fixed neutral filename; ffprobe detects the container from its bytes.
                    os.replace(staging, folder / "source.video")
                    now = time.time()
                    self.db.execute("INSERT INTO jobs(id,original_name,created,updated,profile) VALUES(?,?,?,?,?)",
                                    (job_id, source.name, now, now, profile))
            return job_id
        finally:
            staging.unlink(missing_ok=True)

    def recover(self):
        # Call only after acquiring worker_lock. Rendering/checkpoints are repeatable.
        with self.db:
            self.db.execute("UPDATE jobs SET state='queued', next_run=0, updated=? WHERE state='running'",
                            (time.time(),))
            self.db.execute("UPDATE downloads SET state='queued',next_run=0,updated=? WHERE state='running'", (time.time(),))

    def queue_url(self, url, profile=""):
        from .downloads import normalize_url
        url = normalize_url(url)
        identifier = hashlib.sha256((url + "\0" + profile).encode()).hexdigest()
        now = time.time()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO downloads(id,url,profile,created,updated) VALUES(?,?,?,?,?)", (identifier, url, profile, now, now))
        return identifier

    def claim_download(self):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute("SELECT * FROM downloads WHERE state IN ('queued','retry') AND next_run<=? ORDER BY created LIMIT 1", (time.time(),)).fetchone()
            if row:
                self.db.execute("UPDATE downloads SET state='running',attempts=attempts+1,updated=? WHERE id=?", (time.time(), row["id"]))
        return dict(self.db.execute("SELECT * FROM downloads WHERE id=?", (row["id"],)).fetchone()) if row else None

    def finish_download(self, identifier, job_id):
        with self.db:
            self.db.execute("UPDATE downloads SET state='done',job_id=?,error=NULL,updated=? WHERE id=?", (job_id, time.time(), identifier))

    def fail_download(self, download, message, config):
        state = "failed" if download["attempts"] >= config["max_attempts"] else "retry"
        delay = min(3600, config["retry_seconds"] * 2 ** min(download["attempts"] - 1, 10))
        with self.db:
            self.db.execute("UPDATE downloads SET state=?,error=?,next_run=?,updated=? WHERE id=?", (state, message[:1000], time.time() + delay, time.time(), download["id"]))

    def retry_download(self, identifier):
        with self.db:
            cursor = self.db.execute("UPDATE downloads SET state='queued',attempts=0,next_run=0,error=NULL WHERE id=? AND state IN ('failed','retry')", (identifier,))
        if not cursor.rowcount:
            raise ValueError("No failed or deferred download found")

    def downloads(self):
        return [dict(row) for row in self.db.execute("SELECT * FROM downloads ORDER BY created DESC")]

    def set_control(self, key, value):
        with self.db:
            self.db.execute("INSERT INTO controls(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def get_control(self, key, default=""):
        row = self.db.execute("SELECT value FROM controls WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def claim(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT * FROM jobs WHERE state IN ('queued','retry') AND next_run<=? ORDER BY created LIMIT 1",
                                  (time.time(),)).fetchone()
            if row:
                self.db.execute("UPDATE jobs SET state='running',attempts=attempts+1,updated=? WHERE id=?",
                                (time.time(), row["id"]))
            self.db.commit()
            return dict(self.db.execute("SELECT * FROM jobs WHERE id=?", (row["id"],)).fetchone()) if row else None
        except BaseException:
            self.db.rollback()
            raise

    def finish(self, job_id, result):
        with self.db:
            self.db.execute("UPDATE jobs SET state='done',error=NULL,result=?,updated=? WHERE id=?",
                            (json.dumps(result), time.time(), job_id))

    def fail(self, job, message, config):
        state = "failed" if job["attempts"] >= config["max_attempts"] else "retry"
        delay = min(3600, config["retry_seconds"] * 2 ** min(job["attempts"] - 1, 10))
        with self.db:
            self.db.execute("UPDATE jobs SET state=?,error=?,next_run=?,updated=? WHERE id=?",
                            (state, message[:1000], time.time() + delay, time.time(), job["id"]))

    def defer_quota(self, job_id):
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=0, minute=0, second=5, microsecond=0)
        with self.db:
            self.db.execute("UPDATE jobs SET state='retry',attempts=MAX(0,attempts-1),error='Daily AI request cap reached',next_run=?,updated=? WHERE id=?",
                            (tomorrow.timestamp(), time.time(), job_id))

    def retry(self, job_id):
        with self.db:
            updated = self.db.execute("UPDATE jobs SET state='queued',attempts=0,next_run=0,error=NULL WHERE id=? AND state IN ('failed','retry')", (job_id,))
        if not updated.rowcount:
            raise ValueError("No failed/retry job found for this exact ID")

    def reserve_request(self, limit):
        day = datetime.now(timezone.utc).date().isoformat()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO requests(day,count) VALUES(?,0)", (day,))
            cursor = self.db.execute("UPDATE requests SET count=count+1 WHERE day=? AND (?<=0 OR count<?)", (day, limit, limit))
            if not cursor.rowcount:
                raise DailyLimit()

    def jobs(self):
        return [dict(row) for row in self.db.execute("SELECT * FROM jobs ORDER BY created DESC")]
