from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict
import json
import shutil
import urllib.request
import zipfile


@dataclass
class UpdateCheck:
    current_version: str
    latest_version: str | None
    update_available: bool
    manifest_url: str | None
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


class AutoUpdater:
    """
    Manifest-based updater scaffold.

    Manifest format:
    {
      "version": "1.0.1",
      "zip_url": "https://example.com/release.zip",
      "notes": "..."
    }
    """

    def __init__(self, root: str | Path, current_version: str = "1.0.0"):
        self.root = Path(root).resolve()
        self.current_version = current_version

    def check(self, manifest_url: str | None) -> Dict:
        if not manifest_url:
            return UpdateCheck(self.current_version, None, False, None, "No manifest URL configured.").to_dict()
        with urllib.request.urlopen(manifest_url, timeout=15) as resp:
            manifest = json.loads(resp.read().decode("utf-8"))
        latest = manifest.get("version")
        return UpdateCheck(
            current_version=self.current_version,
            latest_version=latest,
            update_available=bool(latest and latest != self.current_version),
            manifest_url=manifest_url,
            notes=manifest.get("notes", ""),
        ).to_dict()

    def apply_zip_update(self, zip_path: str | Path, backup: bool = True) -> Dict:
        zip_path = Path(zip_path)
        if backup:
            backup_path = self.root.parent / f"{self.root.name}.backup"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(self.root, backup_path)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(self.root)
        return {"ok": True, "applied": str(zip_path)}
