from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict
import os


@dataclass
class OIDCConfig:
    issuer: str
    client_id: str
    audience: str
    jwks_url: str

    def to_dict(self) -> Dict:
        return asdict(self)


class OIDCAuthConfig:
    """
    OIDC/SSO configuration scaffold.

    Full JWT verification requires a JOSE dependency such as python-jose or PyJWT.
    This module validates presence and exposes configuration for integration.
    """

    def __init__(self, config: Dict | None = None):
        cfg = config or {}
        self.config = OIDCConfig(
            issuer=cfg.get("issuer") or os.getenv("OIDC_ISSUER", ""),
            client_id=cfg.get("client_id") or os.getenv("OIDC_CLIENT_ID", ""),
            audience=cfg.get("audience") or os.getenv("OIDC_AUDIENCE", ""),
            jwks_url=cfg.get("jwks_url") or os.getenv("OIDC_JWKS_URL", ""),
        )

    def ready(self) -> Dict:
        missing = [k for k, v in self.config.to_dict().items() if not v]
        return {
            "configured": not missing,
            "missing": missing,
            "config": self.config.to_dict(),
        }
