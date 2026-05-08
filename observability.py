from __future__ import annotations

from pathlib import Path
from typing import Dict
import json
import time

from .database import ServiterDatabase


class MetricsRegistry:
    def __init__(self):
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}

    def inc(self, name: str, amount: int = 1):
        self.counters[name] = self.counters.get(name, 0) + amount

    def gauge(self, name: str, value: float):
        self.gauges[name] = value

    def prometheus(self) -> str:
        lines = []
        for k, v in self.counters.items():
            lines.append(f"# TYPE {k} counter")
            lines.append(f"{k} {v}")
        for k, v in self.gauges.items():
            lines.append(f"# TYPE {k} gauge")
            lines.append(f"{k} {v}")
        return "\n".join(lines) + "\n"

    def json(self) -> Dict:
        return {"counters": self.counters, "gauges": self.gauges}


class Observability:
    def __init__(self, db: ServiterDatabase):
        self.db = db
        self.metrics = MetricsRegistry()

    def collect(self) -> Dict:
        tasks = self.db.query("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
        for row in tasks:
            self.metrics.gauge(f"serviter_tasks_{row['status']}", row["count"])
        self.metrics.gauge("serviter_observed_at", time.time())
        return self.metrics.json()

    def prometheus(self) -> str:
        self.collect()
        return self.metrics.prometheus()
