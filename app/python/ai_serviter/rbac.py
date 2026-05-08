from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set

ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "viewer": {"tasks:read", "health:read"},
    "operator": {"tasks:read", "tasks:create", "tasks:run"},
    "admin": {"tasks:read", "tasks:create", "tasks:run", "tasks:approve", "tasks:reject", "users:manage", "system:override"},
}


@dataclass
class RBAC:
    role_permissions: Dict[str, Set[str]] | None = None

    def __post_init__(self):
        if self.role_permissions is None:
            self.role_permissions = ROLE_PERMISSIONS

    def allowed(self, role: str, permission: str) -> bool:
        return permission in self.role_permissions.get(role, set())
