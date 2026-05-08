from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import os
import re


class DefaultsScanner:
    DEFAULT_PATTERNS = [
        "change-me",
        "admin-change-me",
        "change-this-secret",
        "dev-secret-change-me",
        "password",
        "your-key",
    ]

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def scan_files(self) -> Dict:
        findings: List[Dict] = []
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__"} for part in path.parts):
                continue
            if path.suffix.lower() not in {".py", ".yml", ".yaml", ".json", ".md", ".env", ".txt", ".sh", ".service"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                lower = line.lower()
                for pattern in self.DEFAULT_PATTERNS:
                    if pattern in lower:
                        findings.append({
                            "path": str(path.relative_to(self.root)),
                            "line": line_no,
                            "pattern": pattern,
                            "snippet": line.strip()[:180],
                        })
        return {"ok": not findings, "findings": findings}

    def scan_environment(self) -> Dict:
        checks = {
            "SERVITER_SECRET": os.getenv("SERVITER_SECRET", ""),
            "SERVITER_ADMIN_PASSWORD": os.getenv("SERVITER_ADMIN_PASSWORD", ""),
        }
        findings = []
        for key, value in checks.items():
            if not value:
                findings.append({"name": key, "problem": "missing"})
            elif value.lower() in self.DEFAULT_PATTERNS or len(value) < 12:
                findings.append({"name": key, "problem": "weak_or_default"})
        return {"ok": not findings, "findings": findings}
