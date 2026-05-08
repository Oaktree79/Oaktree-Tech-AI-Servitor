from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict
import os
import socket
import time

from .runtime import ServiterRuntime


@dataclass
class WorkerHeartbeat:
    worker_id: str
    host: str
    pid: int
    last_seen: float

    def to_dict(self) -> Dict:
        return asdict(self)


class DistributedWorker:
    """
    SQLite-backed distributed worker scaffold.

    Multiple workers may poll the same SQLite DB on shared storage for lab use.
    For production, replace this with Postgres/Redis/NATS/SQS.
    """

    def __init__(self, root: str | Path, worker_id: str | None = None):
        self.root = Path(root).resolve()
        self.worker_id = worker_id or f"{socket.gethostname()}-{os.getpid()}"
        self.runtime = ServiterRuntime(self.root)
        self._init_table()

    def _init_table(self):
        self.runtime.db.execute("""
        CREATE TABLE IF NOT EXISTS worker_heartbeats (
          worker_id TEXT PRIMARY KEY,
          host TEXT NOT NULL,
          pid INTEGER NOT NULL,
          last_seen REAL NOT NULL
        )
        """)

    def heartbeat(self) -> Dict:
        hb = WorkerHeartbeat(self.worker_id, socket.gethostname(), os.getpid(), time.time())
        self.runtime.db.execute(
            """
            INSERT INTO worker_heartbeats(worker_id,host,pid,last_seen)
            VALUES(?,?,?,?)
            ON CONFLICT(worker_id) DO UPDATE SET host=excluded.host,pid=excluded.pid,last_seen=excluded.last_seen
            """,
            (hb.worker_id, hb.host, hb.pid, hb.last_seen),
        )
        return hb.to_dict()

    def run_once(self) -> Dict:
        self.heartbeat()
        return self.runtime.run_once()

    def workers(self):
        return self.runtime.db.query("SELECT * FROM worker_heartbeats ORDER BY last_seen DESC")
