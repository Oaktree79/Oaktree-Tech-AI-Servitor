from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from datetime import datetime, timezone
import csv
import json
import re
import ssl
import socket


DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%d/%m/%Y",
    "%b %d %Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
]


@dataclass
class CertificateRecord:
    raw: Dict[str, str]
    common_name: str = ""
    subject: str = ""
    issuer: str = ""
    serial_number: str = ""
    not_before: str = ""
    not_after: str = ""
    san: str = ""
    source: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CertificateFinding:
    severity: str
    kind: str
    message: str
    certificate: Dict

    def to_dict(self) -> Dict:
        return asdict(self)


class CertificateInventory:
    """
    CSV-backed certificate inventory.

    The loader is schema-tolerant: it maps common column names such as:
    common_name, cn, subject, issuer, serial_number, not_after, expiry, expires,
    san, dns_names, source, host.
    """

    FIELD_ALIASES = {
        "common_name": ["common_name", "cn", "common name", "name", "domain", "host", "hostname"],
        "subject": ["subject", "subject_dn", "subject dn"],
        "issuer": ["issuer", "issuer_dn", "issuer dn", "ca"],
        "serial_number": ["serial", "serial_number", "serial number"],
        "not_before": ["not_before", "valid_from", "start_date", "valid from"],
        "not_after": ["not_after", "valid_to", "expiry", "expires", "expiration", "expiration_date", "valid until"],
        "san": ["san", "subject_alt_names", "subject alternative names", "dns_names", "dns names"],
        "source": ["source", "scanner", "file", "path"],
    }

    def __init__(self):
        self.records: List[CertificateRecord] = []

    def load_csv(self, path: str | Path) -> "CertificateInventory":
        path = Path(path)
        with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample) if sample.strip() else csv.excel
            reader = csv.DictReader(f, dialect=dialect)
            self.records = [self._map_row(row) for row in reader]
        return self

    def _map_row(self, row: Dict[str, str]) -> CertificateRecord:
        normalized = {self._norm(k): (v or "").strip() for k, v in row.items()}

        def get(field: str) -> str:
            for alias in self.FIELD_ALIASES[field]:
                if self._norm(alias) in normalized:
                    return normalized[self._norm(alias)]
            return ""

        return CertificateRecord(
            raw=dict(row),
            common_name=get("common_name"),
            subject=get("subject"),
            issuer=get("issuer"),
            serial_number=get("serial_number"),
            not_before=get("not_before"),
            not_after=get("not_after"),
            san=get("san"),
            source=get("source"),
        )

    def _norm(self, key: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", (key or "").lower()).strip("_")

    def summary(self) -> Dict:
        issuers: Dict[str, int] = {}
        expired = 0
        expiring_30 = 0
        missing_expiry = 0

        for rec in self.records:
            if rec.issuer:
                issuers[rec.issuer] = issuers.get(rec.issuer, 0) + 1
            days = self.days_until_expiry(rec)
            if days is None:
                missing_expiry += 1
            elif days < 0:
                expired += 1
            elif days <= 30:
                expiring_30 += 1

        return {
            "total_certificates": len(self.records),
            "expired": expired,
            "expiring_within_30_days": expiring_30,
            "missing_expiry": missing_expiry,
            "issuer_count": len(issuers),
            "top_issuers": sorted(issuers.items(), key=lambda x: x[1], reverse=True)[:10],
        }

    def parse_date(self, value: str) -> Optional[datetime]:
        value = (value or "").strip()
        if not value:
            return None
        # Try ISO parser first
        try:
            cleaned = value.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(cleaned)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except Exception:
            pass

        for fmt in DATE_FORMATS:
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.replace(tzinfo=timezone.utc)
            except Exception:
                continue
        return None

    def days_until_expiry(self, rec: CertificateRecord) -> Optional[int]:
        dt = self.parse_date(rec.not_after)
        if not dt:
            return None
        now = datetime.now(timezone.utc)
        return int((dt - now).total_seconds() // 86400)

    def findings(self, warn_days: int = 30) -> List[CertificateFinding]:
        results: List[CertificateFinding] = []
        seen_serials = {}

        for rec in self.records:
            cert = rec.to_dict()
            days = self.days_until_expiry(rec)

            if days is None:
                results.append(CertificateFinding(
                    severity="medium",
                    kind="missing_expiry",
                    message="Certificate has no recognized expiry date.",
                    certificate=cert,
                ))
            elif days < 0:
                results.append(CertificateFinding(
                    severity="critical",
                    kind="expired",
                    message=f"Certificate expired {-days} days ago.",
                    certificate=cert,
                ))
            elif days <= warn_days:
                results.append(CertificateFinding(
                    severity="high",
                    kind="expiring_soon",
                    message=f"Certificate expires in {days} days.",
                    certificate=cert,
                ))

            if rec.serial_number:
                if rec.serial_number in seen_serials:
                    results.append(CertificateFinding(
                        severity="medium",
                        kind="duplicate_serial",
                        message="Duplicate certificate serial number found in inventory.",
                        certificate=cert,
                    ))
                seen_serials[rec.serial_number] = True

            if rec.common_name and "*" in rec.common_name:
                results.append(CertificateFinding(
                    severity="low",
                    kind="wildcard_certificate",
                    message="Wildcard certificate found; confirm scope and rotation policy.",
                    certificate=cert,
                ))

        return results

    def export_json(self, path: str | Path):
        data = {
            "summary": self.summary(),
            "records": [r.to_dict() for r in self.records],
            "findings": [f.to_dict() for f in self.findings()],
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def search(self, query: str) -> List[CertificateRecord]:
        q = query.lower()
        return [
            r for r in self.records
            if q in json.dumps(r.to_dict(), default=str).lower()
        ]


class LiveCertificateChecker:
    """
    Fetches live TLS certificate metadata from a host.
    """

    def fetch(self, host: str, port: int = 443, timeout: int = 10) -> Dict:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        return {
            "host": host,
            "port": port,
            "certificate": cert,
        }
