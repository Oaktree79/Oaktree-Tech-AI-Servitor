from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict
import os


@dataclass
class PostgresConfig:
    host: str
    port: int
    database: str
    user: str
    sslmode: str

    def dsn_without_password(self) -> str:
        return f"postgresql://{self.user}@{self.host}:{self.port}/{self.database}?sslmode={self.sslmode}"

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["dsn"] = self.dsn_without_password()
        return data


class ProductionDatabaseConfig:
    """
    PostgreSQL production database configuration scaffold.

    The runtime still supports SQLite for local dev. Use this module to validate
    production env before swapping the database adapter to psycopg/SQLAlchemy.
    """

    def __init__(self):
        self.config = PostgresConfig(
            host=os.getenv("POSTGRES_HOST", ""),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", ""),
            user=os.getenv("POSTGRES_USER", ""),
            sslmode=os.getenv("POSTGRES_SSLMODE", "require"),
        )
        self.password_present = bool(os.getenv("POSTGRES_PASSWORD", ""))

    def validate(self) -> Dict:
        missing = []
        for key, value in self.config.to_dict().items():
            if key != "dsn" and not value:
                missing.append(key)
        if not self.password_present:
            missing.append("password")
        return {
            "ok": not missing,
            "missing": missing,
            "config": self.config.to_dict(),
            "password_present": self.password_present,
        }
