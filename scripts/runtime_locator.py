from __future__ import annotations

from pathlib import Path
import os
import shutil
import sys


def find_python(base_dir: str | Path) -> str:
    base = Path(base_dir).resolve()
    candidates = [
        base / "installer" / "runtime" / "python" / "python.exe",
        base / "runtime" / "python" / "python.exe",
        base / "installer" / "runtime" / "python" / "bin" / "python3",
        base / "runtime" / "python" / "bin" / "python3",
    ]
    for c in candidates:
        if c.exists():
            return str(c)

    for name in ["python3", "python"]:
        found = shutil.which(name)
        if found:
            return found

    raise RuntimeError("Python runtime not found. Install Python 3.10+ or add bundled runtime.")


if __name__ == "__main__":
    print(find_python(Path(__file__).resolve().parents[2]))
