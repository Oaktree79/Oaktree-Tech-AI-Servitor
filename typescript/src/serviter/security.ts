import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

export type SecurityFinding = {
  path: string;
  line: number;
  kind: string;
  severity: "medium" | "high" | "critical";
  snippet: string;
};

const patterns: [string, RegExp, SecurityFinding["severity"]][] = [
  ["possible_api_key", /(api[_-]?key|secret|token|password)\s*[:=]\s*['"][^'"]{8,}['"]/i, "critical"],
  ["javascript_eval", /\beval\s*\(/, "high"],
  ["inner_html_assignment", /\.innerHTML\s*=/, "medium"],
];

export class SecurityScanner {
  public findings: SecurityFinding[] = [];

  constructor(public root: string) {}

  scan(): this {
    this.findings = [];
    this.walk(this.root);
    return this;
  }

  private walk(current: string): void {
    for (const entry of readdirSync(current)) {
      if ([".git", "node_modules", "dist", "build"].includes(entry)) continue;
      const full = join(current, entry);
      const stat = statSync(full);
      if (stat.isDirectory()) {
        this.walk(full);
      } else if (/\.(ts|tsx|js|jsx|json|md)$/.test(full)) {
        this.scanFile(full);
      }
    }
  }

  private scanFile(full: string): void {
    const rel = relative(this.root, full);
    const lines = readFileSync(full, "utf8").split(/\r?\n/);
    lines.forEach((line, i) => {
      for (const [kind, pattern, severity] of patterns) {
        if (pattern.test(line)) {
          this.findings.push({ path: rel, line: i + 1, kind, severity, snippet: line.trim().slice(0, 180) });
        }
      }
    });
  }
}
