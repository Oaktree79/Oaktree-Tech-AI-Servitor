from __future__ import annotations

from dataclasses import dataclass, asdict
from urllib.parse import urlparse
from typing import Dict, List
import fnmatch
import socket


@dataclass
class NetworkDecision:
    allowed: bool
    reason: str
    host: str

    def to_dict(self) -> Dict:
        return asdict(self)


class NetworkPolicy:
    """
    Egress policy checker.

    This does not firewall the OS by itself. It is used by tools before making
    outbound calls. Pair with Docker/Kubernetes network policies for enforcement.
    """

    def __init__(self, allowed_hosts: List[str] | None = None, blocked_hosts: List[str] | None = None):
        self.allowed_hosts = allowed_hosts or ["api.openai.com", "*.github.com", "github.com", "*.gitlab.com", "gitlab.com"]
        self.blocked_hosts = blocked_hosts or ["169.254.169.254", "metadata.google.internal", "localhost", "127.*", "10.*", "192.168.*", "172.16.*"]

    def check_url(self, url: str) -> Dict:
        host = urlparse(url).hostname or url
        return self.check_host(host).to_dict()

    def check_host(self, host: str) -> NetworkDecision:
        if any(fnmatch.fnmatch(host, pat) for pat in self.blocked_hosts):
            return NetworkDecision(False, "host matches blocked pattern", host)
        if any(fnmatch.fnmatch(host, pat) for pat in self.allowed_hosts):
            return NetworkDecision(True, "host allowed", host)
        return NetworkDecision(False, "host not in allowlist", host)
