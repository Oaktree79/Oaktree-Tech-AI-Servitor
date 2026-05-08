from __future__ import annotations

from pathlib import Path
from typing import Dict
import json
import tempfile

from .runtime import ServiterRuntime
from .certificate_manager import CertificateInventory
from .network_policy import NetworkPolicy


class IntegrationHarness:
    """
    End-to-end local integration harness.

    Exercises:
    - runtime
    - queue
    - worker
    - certificate inventory
    - metrics
    - network policy
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def run_smoke(self) -> Dict:
        runtime = ServiterRuntime(self.root)
        task = runtime.submit("analyze project")
        worker = runtime.run_once()
        metrics = runtime.observability.collect()
        net = NetworkPolicy().check_url("https://github.com")

        return {
            "task": task.__dict__,
            "worker": worker,
            "metrics": metrics,
            "network_policy": net,
            "ok": worker.get("status") in {"succeeded", "idle"} and net["allowed"] is True,
        }

    def run_certificate_smoke(self) -> Dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "certs.csv"
            path.write_text("Common Name,Issuer,Expiration Date\nexample.com,CA,2099-01-01\n", encoding="utf-8")
            inv = CertificateInventory().load_csv(path)
            return {"summary": inv.summary(), "findings": [f.to_dict() for f in inv.findings()]}
