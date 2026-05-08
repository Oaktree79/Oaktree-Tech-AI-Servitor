from __future__ import annotations
from pathlib import Path
from typing import Dict
import hashlib, hmac

class UpdateSecurity:
    def sha256(self, path: str | Path) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def verify_sha256(self, path: str | Path, expected: str) -> Dict:
        actual = self.sha256(path)
        return {"ok": hmac.compare_digest(actual, expected), "actual": actual, "expected": expected}

    def hmac_sign(self, path: str | Path, secret: str) -> str:
        digest = hmac.new(secret.encode(), digestmod=hashlib.sha256)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def hmac_verify(self, path: str | Path, secret: str, signature: str) -> Dict:
        actual = self.hmac_sign(path, secret)
        return {"ok": hmac.compare_digest(actual, signature), "actual": actual}
