from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional
import os
import subprocess
import tempfile
import time


@dataclass
class SandboxResult:
    command: List[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


class ToolSandbox:
    """
    Local command sandbox with allowlist and timeout.

    This is a development sandbox, not a hardened container boundary.
    For production, run this behind Docker/firecracker/gVisor or a remote worker.
    """

    def __init__(self, root: str | Path, allowed_commands: Optional[set[str]] = None, timeout_seconds: int = 60):
        self.root = Path(root).resolve()
        self.allowed_commands = allowed_commands or {"python", "python3", "pytest", "npm", "node", "echo"}
        self.timeout_seconds = timeout_seconds

    def run(self, command: List[str], cwd: str | Path | None = None, env: Optional[Dict[str, str]] = None) -> SandboxResult:
        if not command:
            raise ValueError("Command cannot be empty")

        executable = Path(command[0]).name
        if executable not in self.allowed_commands:
            raise PermissionError(f"Command not allowed: {executable}")

        run_cwd = Path(cwd).resolve() if cwd else self.root
        if self.root not in run_cwd.parents and run_cwd != self.root:
            raise PermissionError(f"cwd must stay inside project root: {run_cwd}")

        safe_env = {
            "PATH": os.getenv("PATH", ""),
            "HOME": tempfile.gettempdir(),
            "PYTHONNOUSERSITE": "1",
        }
        if env:
            safe_env.update(env)

        started = time.time()
        try:
            proc = subprocess.run(
                command,
                cwd=run_cwd,
                env=safe_env,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            return SandboxResult(
                command=command,
                cwd=str(run_cwd),
                returncode=proc.returncode,
                stdout=proc.stdout[-10000:],
                stderr=proc.stderr[-10000:],
                duration_seconds=time.time() - started,
            )
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(
                command=command,
                cwd=str(run_cwd),
                returncode=124,
                stdout=(exc.stdout or "")[-10000:] if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "")[-10000:] if isinstance(exc.stderr, str) else "",
                duration_seconds=time.time() - started,
                timed_out=True,
            )
