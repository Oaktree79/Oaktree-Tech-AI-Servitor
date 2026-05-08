from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import json
import re


SECRET_PATTERNS = {
    "possible_api_key": re.compile(r"""(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['"][^'"]{8,}['"]"""),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "jwt_token": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
}

DANGEROUS_PATTERNS = {
    "python_eval_exec": re.compile(r"\b(eval|exec)\s*\("),
    "shell_true": re.compile(r"shell\s*=\s*True"),
    "pickle_load": re.compile(r"\bpickle\.loads?\s*\("),
    "yaml_unsafe_load": re.compile(r"\byaml\.load\s*\("),
    "hardcoded_bind_all_interfaces": re.compile(r"0\.0\.0\.0"),
    "sql_string_concat": re.compile(r"(SELECT|INSERT|UPDATE|DELETE).*\+.*(FROM|INTO|WHERE|SET)", re.IGNORECASE),
    "javascript_eval": re.compile(r"\beval\s*\("),
    "inner_html_assignment": re.compile(r"\.innerHTML\s*="),
}


@dataclass
class SecurityFinding:
    path: str
    line: int
    kind: str
    severity: str
    snippet: str
    recommendation: str

    def to_dict(self) -> Dict:
        return asdict(self)


class SecurityScanner:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.findings: List[SecurityFinding] = []

    def scan(self) -> "SecurityScanner":
        self.findings.clear()
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__", ".serviter"} for part in path.parts):
                continue
            if path.suffix.lower() not in {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".env", ".txt", ".md", ".yaml", ".yml"}:
                continue
            self._scan_file(path)
        return self

    def _scan_file(self, path: Path):
        rel = str(path.relative_to(self.root))
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").replace("\\n", "\n")
            lines = content.splitlines()
        except Exception:
            return

        for idx, line in enumerate(lines, start=1):
            for kind, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    self.findings.append(SecurityFinding(
                        path=rel,
                        line=idx,
                        kind=kind,
                        severity="critical",
                        snippet=self._redact(line.strip()),
                        recommendation="Remove the secret, rotate it, and load credentials from a secret manager or environment variable.",
                    ))

            for kind, pattern in DANGEROUS_PATTERNS.items():
                if pattern.search(line):
                    self.findings.append(SecurityFinding(
                        path=rel,
                        line=idx,
                        kind=kind,
                        severity=self._severity(kind),
                        snippet=line.strip()[:180],
                        recommendation=self._recommendation(kind),
                    ))

    def _redact(self, line: str) -> str:
        if len(line) <= 16:
            return "[REDACTED]"
        return line[:8] + "...[REDACTED]..." + line[-4:]

    def _severity(self, kind: str) -> str:
        if kind in {"python_eval_exec", "shell_true", "pickle_load", "yaml_unsafe_load", "javascript_eval"}:
            return "high"
        return "medium"

    def _recommendation(self, kind: str) -> str:
        recs = {
            "python_eval_exec": "Avoid eval/exec. Use explicit parsers or dispatch tables.",
            "shell_true": "Avoid shell=True. Pass arguments as a list and validate inputs.",
            "pickle_load": "Avoid pickle for untrusted data. Use JSON or a signed format.",
            "yaml_unsafe_load": "Use yaml.safe_load instead of yaml.load.",
            "inner_html_assignment": "Avoid innerHTML with untrusted content. Use textContent or sanitization.",
            "sql_string_concat": "Use parameterized SQL queries.",
        }
        return recs.get(kind, "Review this pattern for security risk.")

    def to_json(self) -> str:
        return json.dumps({"findings": [f.to_dict() for f in self.findings]}, indent=2)
