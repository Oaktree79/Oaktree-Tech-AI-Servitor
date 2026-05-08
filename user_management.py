from __future__ import annotations

from typing import Dict, List

from .auth import AuthManager
from .database import ServiterDatabase


class UserManagement:
    def __init__(self, db: ServiterDatabase):
        self.db = db
        self.auth = AuthManager(db)

    def create_user(self, username: str, password: str, role: str = "operator") -> Dict:
        self.auth.create_user(username, password, role)
        self.db.add_event(None, "user_created", {"username": username, "role": role})
        return {"username": username, "role": role}

    def list_users(self) -> List[Dict]:
        rows = self.db.query("SELECT username, role, created_at FROM users ORDER BY username")
        return rows

    def set_role(self, username: str, role: str) -> Dict:
        self.db.execute("UPDATE users SET role=? WHERE username=?", (role, username))
        self.db.add_event(None, "user_role_updated", {"username": username, "role": role})
        return {"username": username, "role": role}

    def delete_user(self, username: str) -> Dict:
        self.db.execute("DELETE FROM users WHERE username=?", (username,))
        self.db.add_event(None, "user_deleted", {"username": username})
        return {"username": username, "deleted": True}
