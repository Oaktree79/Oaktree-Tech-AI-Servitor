from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import base64
import hashlib
import hmac
import os
import secrets
import time

from .database import ServiterDatabase


@dataclass
class User:
    username: str
    role: str


class AuthManager:
    def __init__(self, db: ServiterDatabase, secret: str | None = None):
        self.db = db
        self.secret = (secret or os.getenv("SERVITER_SECRET") or "dev-secret-change-me").encode("utf-8")

    def hash_password(self, password: str, salt: str | None = None) -> str:
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
        return f"pbkdf2_sha256${salt}${base64.b64encode(digest).decode()}"

    def verify_password(self, password: str, stored: str) -> bool:
        scheme, salt, digest = stored.split("$", 2)
        expected = self.hash_password(password, salt)
        return hmac.compare_digest(expected, stored)

    def create_user(self, username: str, password: str, role: str = "operator"):
        self.db.execute(
            "INSERT OR REPLACE INTO users(username,password_hash,role,created_at) VALUES(?,?,?,?)",
            (username, self.hash_password(password), role, time.time()),
        )

    def authenticate(self, username: str, password: str) -> Optional[User]:
        rows = self.db.query("SELECT * FROM users WHERE username=?", (username,))
        if not rows:
            return None
        row = rows[0]
        if not self.verify_password(password, row["password_hash"]):
            return None
        return User(username=row["username"], role=row["role"])

    def issue_token(self, user: User, ttl_seconds: int = 86400) -> str:
        expiry = int(time.time()) + ttl_seconds
        payload = f"{user.username}:{user.role}:{expiry}"
        sig = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
        return base64.urlsafe_b64encode(f"{payload}:{sig}".encode()).decode()

    def verify_token(self, token: str) -> Optional[User]:
        try:
            raw = base64.urlsafe_b64decode(token.encode()).decode()
            username, role, expiry, sig = raw.rsplit(":", 3)
            payload = f"{username}:{role}:{expiry}"
            expected = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, sig):
                return None
            if int(expiry) < int(time.time()):
                return None
            return User(username=username, role=role)
        except Exception:
            return None
