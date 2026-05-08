from __future__ import annotations
from pathlib import Path
import argparse, urllib.request, zipfile

WINDOWS_EMBED_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"

def fetch_windows_runtime(root: Path, url: str = WINDOWS_EMBED_URL):
    target = root / "installer" / "runtime" / "python"
    archive = root / "installer" / "runtime" / "python-windows-embed.zip"
    if target.exists():
        return {"ok": True, "runtime": str(target), "already_exists": True}
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as resp:
        archive.write_bytes(resp.read())
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "r") as z:
        z.extractall(target)
    for pth in target.glob("python*._pth"):
        pth.write_text(pth.read_text(encoding="utf-8").replace("#import site", "import site"), encoding="utf-8")
    return {"ok": True, "runtime": str(target), "archive": str(archive)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--url", default=WINDOWS_EMBED_URL)
    args = p.parse_args()
    print(fetch_windows_runtime(Path(args.root).resolve(), args.url))

if __name__ == "__main__":
    main()
