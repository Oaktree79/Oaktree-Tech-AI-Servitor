from __future__ import annotations

from pathlib import Path
from typing import Dict
import os
import subprocess
import sys
import time
import webbrowser

from .config_wizard import ConfigWizard


class AutoLauncher:
    """
    Starts API server and opens dashboard/browser.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.config = ConfigWizard(root).load()

    def launch_api(self) -> Dict:
        host = self.config.get("host", "127.0.0.1")
        port = str(self.config.get("port", 8765))
        cmd = [sys.executable, "-m", "ai_serviter.service", "--root", str(self.root), "--mode", "api", "--host", host, "--port", port]
        log_dir = self.root / "logs"
        log_dir.mkdir(exist_ok=True)
        log = open(log_dir / "api.log", "a", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=self.root / "python", stdout=log, stderr=log)
        return {"pid": proc.pid, "url": f"http://{host}:{port}", "command": cmd}

    def open_dashboard(self) -> Dict:
        host = self.config.get("host", "127.0.0.1")
        port = self.config.get("port", 8765)
        url = f"http://{host}:{port}"
        webbrowser.open(url)
        return {"opened": url}

    def launch_all(self) -> Dict:
        api = self.launch_api()
        time.sleep(2)
        opened = self.open_dashboard() if self.config.get("open_dashboard_on_start", True) else None
        return {"api": api, "dashboard": opened}
