from __future__ import annotations

from pathlib import Path
from typing import Dict
import json
import tarfile
import time

from .runtime import ServiterRuntime


class MonitoringBackupValidator:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def validate_metrics(self) -> Dict:
        runtime = ServiterRuntime(self.root)
        prometheus = runtime.observability.prometheus()
        return {
            "ok": "serviter_observed_at" in prometheus,
            "prometheus_preview": prometheus[:1000],
        }

    def create_backup(self, output_dir: str | Path = "backups") -> Dict:
        output = self.root / output_dir
        output.mkdir(parents=True, exist_ok=True)
        target = output / f"serviter-backup-{int(time.time())}.tar.gz"
        source = self.root / ".serviter"
        if not source.exists():
            source.mkdir(parents=True, exist_ok=True)
            (source / "README.txt").write_text("empty backup seed\n", encoding="utf-8")
        with tarfile.open(target, "w:gz") as tar:
            tar.add(source, arcname=".serviter")
        return {"ok": target.exists(), "backup": str(target), "size_bytes": target.stat().st_size}

    def validate_backup_readable(self, backup_path: str | Path) -> Dict:
        backup = Path(backup_path)
        try:
            with tarfile.open(backup, "r:gz") as tar:
                names = tar.getnames()
            return {"ok": True, "entries": names[:50]}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
