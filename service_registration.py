from __future__ import annotations

from pathlib import Path
from typing import Dict
import os
import platform
import subprocess
import textwrap


class ServiceRegistrar:
    """
    Generates and optionally installs OS services.

    Safe default: write service files/scripts only. Installation requires explicit command.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def generate(self) -> Dict:
        system = platform.system().lower()
        if "windows" in system:
            return self.generate_windows()
        if "darwin" in system:
            return self.generate_macos()
        return self.generate_linux()

    def generate_linux(self) -> Dict:
        out = self.root / "installer" / "linux" / "ai-serviter.service"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(textwrap.dedent(f"""
        [Unit]
        Description=AI Serviter
        After=network.target

        [Service]
        Type=simple
        WorkingDirectory={self.root}
        EnvironmentFile={self.root}/.serviter/.env
        ExecStart={self.root}/.venv/bin/serviter-service --root {self.root} --mode api --host 127.0.0.1 --port 8765
        Restart=always
        RestartSec=5

        [Install]
        WantedBy=multi-user.target
        """).strip() + "\n", encoding="utf-8")
        return {"platform": "linux", "service_file": str(out)}

    def generate_windows(self) -> Dict:
        out = self.root / "installer" / "windows" / "install_service.ps1"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(textwrap.dedent(f"""
        $Root = "{self.root}"
        $Python = "$Root\\.venv\\Scripts\\serviter-service.exe"
        New-Service -Name "AIServiter" -BinaryPathName "`"$Python`" --root `"$Root`" --mode api --host 127.0.0.1 --port 8765" -DisplayName "AI Serviter" -StartupType Automatic
        Start-Service AIServiter
        """).strip() + "\n", encoding="utf-8")
        return {"platform": "windows", "script": str(out)}

    def generate_macos(self) -> Dict:
        out = self.root / "installer" / "macos" / "com.aiserviter.plist"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(textwrap.dedent(f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
          <key>Label</key><string>com.aiserviter</string>
          <key>ProgramArguments</key>
          <array>
            <string>{self.root}/.venv/bin/serviter-service</string>
            <string>--root</string><string>{self.root}</string>
            <string>--mode</string><string>api</string>
            <string>--host</string><string>127.0.0.1</string>
            <string>--port</string><string>8765</string>
          </array>
          <key>RunAtLoad</key><true/>
          <key>KeepAlive</key><true/>
        </dict>
        </plist>
        """).strip() + "\n", encoding="utf-8")
        return {"platform": "macos", "plist": str(out)}
