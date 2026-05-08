from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import shutil
import subprocess
import time


@dataclass
class ContainerSandboxResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float

    def to_dict(self) -> Dict:
        return asdict(self)


class DockerSandbox:
    """
    Hardened sandbox scaffold using Docker.

    Uses:
    - network disabled by default
    - read/write project mount
    - memory/pids limits
    - dropped capabilities
    - no-new-privileges

    Requires Docker installed on host.
    """

    def __init__(
        self,
        root: str | Path,
        image: str = "python:3.11-slim",
        timeout_seconds: int = 120,
        network: str = "none",
        memory: str = "512m",
        pids_limit: int = 256,
    ):
        self.root = Path(root).resolve()
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.network = network
        self.memory = memory
        self.pids_limit = pids_limit

    def available(self) -> bool:
        return shutil.which("docker") is not None

    def run(self, command: List[str]) -> ContainerSandboxResult:
        if not self.available():
            raise RuntimeError("Docker is not available")

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", self.network,
            "--memory", self.memory,
            "--pids-limit", str(self.pids_limit),
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "-v", f"{self.root}:/workspace",
            "-w", "/workspace",
            self.image,
            *command,
        ]
        started = time.time()
        proc = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        return ContainerSandboxResult(
            command=docker_cmd,
            returncode=proc.returncode,
            stdout=proc.stdout[-10000:],
            stderr=proc.stderr[-10000:],
            duration_seconds=time.time() - started,
        )
