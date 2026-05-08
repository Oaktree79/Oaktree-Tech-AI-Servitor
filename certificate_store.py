from __future__ import annotations

from pathlib import Path
from typing import Dict
import json
import time

from .certificate_manager import CertificateInventory
from .database import ServiterDatabase


CERT_SCHEMA = """
CREATE TABLE IF NOT EXISTS certificate_imports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_path TEXT,
  summary_json TEXT NOT NULL,
  findings_json TEXT NOT NULL,
  created_at REAL NOT NULL
);
"""


class CertificateStore:
    def __init__(self, db: ServiterDatabase):
        self.db = db
        with self.db.connect() as con:
            con.executescript(CERT_SCHEMA)

    def import_csv(self, path: str | Path) -> Dict:
        inv = CertificateInventory().load_csv(path)
        summary = inv.summary()
        findings = [f.to_dict() for f in inv.findings()]
        self.db.execute(
            """
            INSERT INTO certificate_imports(source_path,summary_json,findings_json,created_at)
            VALUES(?,?,?,?)
            """,
            (str(path), json.dumps(summary), json.dumps(findings), time.time()),
        )
        self.db.add_event(None, "certificate_inventory_imported", {
            "source_path": str(path),
            "summary": summary,
            "finding_count": len(findings),
        })
        return {"summary": summary, "findings": findings}

    def latest(self) -> Dict:
        rows = self.db.query("SELECT * FROM certificate_imports ORDER BY created_at DESC LIMIT 1")
        if not rows:
            return {"summary": None, "findings": []}
        row = rows[0]
        return {
            "id": row["id"],
            "source_path": row["source_path"],
            "summary": json.loads(row["summary_json"]),
            "findings": json.loads(row["findings_json"]),
            "created_at": row["created_at"],
        }
