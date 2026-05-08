import { readFileSync, readdirSync, statSync } from "node:fs";
import { extname, join, relative } from "node:path";

export type SymbolRecord = {
  name: string;
  kind: string;
  path: string;
  line: number;
  signature?: string;
};

const ignoreDirs = new Set([".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"]);

export class CodeIndex {
  public symbols: SymbolRecord[] = [];

  constructor(public root: string) {}

  build(): this {
    this.symbols = [];
    this.walk(this.root);
    return this;
  }

  private walk(current: string): void {
    for (const entry of readdirSync(current)) {
      if (ignoreDirs.has(entry)) continue;
      const full = join(current, entry);
      const stat = statSync(full);
      if (stat.isDirectory()) {
        this.walk(full);
      } else if ([".ts", ".tsx", ".js", ".jsx"].includes(extname(full))) {
        this.indexFile(full);
      }
    }
  }

  private indexFile(full: string): void {
    const rel = relative(this.root, full);
    const lines = readFileSync(full, "utf8").split(/\r?\n/);

    lines.forEach((line, i) => {
      const trimmed = line.trim();
      const match =
        trimmed.match(/export\s+class\s+(\w+)/) ||
        trimmed.match(/class\s+(\w+)/) ||
        trimmed.match(/export\s+function\s+(\w+)/) ||
        trimmed.match(/function\s+(\w+)/) ||
        trimmed.match(/export\s+const\s+(\w+)/);

      if (match) {
        this.symbols.push({
          name: match[1],
          kind: trimmed.includes("class") ? "class" : "function_or_export",
          path: rel,
          line: i + 1,
          signature: trimmed.slice(0, 180),
        });
      }
    });
  }

  search(query: string): SymbolRecord[] {
    const q = query.toLowerCase();
    return this.symbols.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.path.toLowerCase().includes(q) ||
        (s.signature ?? "").toLowerCase().includes(q),
    );
  }
}
