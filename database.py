from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sqlite3
import time


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  instruction TEXT NOT NULL,
  status TEXT NOT NULL,
  priority INTEGER DEFAULT 100,
  requires_approval INTEGER DEFAULT 1,
  approval_status TEXT DEFAULT 'pending',
  result_json TEXT,
  error TEXT,
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT,
  event_type TEXT NOT NULL,
  payload_json TEXT,
  created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS approvals (
  task_id TEXT PRIMARY KEY,
  approved_by TEXT,
  approved_at REAL,
  status TEXT NOT NULL,
  reason TEXT
);

CREATE TABLE IF NOT EXISTS users (
  username TEXT PRIMARY KEY,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  created_at REAL NOT NULL
);
"""


class ServiterDatabase:
    def __init__(self, path: str | Path = ".serviter/serviter.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def init(self):
        with self.connect() as con:
            con.executescript(SCHEMA)

    def execute(self, sql: str, params: tuple = ()):
        with self.connect() as con:
            con.execute(sql, params)
            con.commit()

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def add_event(self, task_id: Optional[str], event_type: str, payload: Dict[str, Any] | None = None):
        self.execute(
            "INSERT INTO events(task_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
            (task_id, event_type, json.dumps(payload or {}), time.time()),
        )
