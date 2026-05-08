import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

export type MemoryHit = {
  score: number;
  path: string;
  snippet: string;
};

function tokens(text: string): string[] {
  return text.toLowerCase().match(/[a-z_][a-z0-9_]{1,}/g) ?? [];
}

function score(query: string, text: string): number {
  const q = new Set(tokens(query));
  const t = tokens(text);
  if (!q.size || !t.length) return 0;
  let hits = 0;
  for (const token of t) if (q.has(token)) hits += 1;
  return hits / Math.sqrt(t.length);
}

export class VectorMemory {
  public docs: { path: string; text: string }[] = [];

  constructor(public root: string) {}

  build(): this {
    this.docs = [];
    this.walk(this.root);
    return this;
  }

  private walk(current: string): void {
    for (const entry of readdirSync(current)) {
      if ([".git", "node_modules", "dist", "build"].includes(entry)) continue;
      const full = join(current, entry);
      const stat = statSync(full);
      if (stat.isDirectory()) this.walk(full);
      else if (/\.(ts|tsx|js|jsx|json|md)$/.test(full)) {
        this.docs.push({ path: relative(this.root, full), text: readFileSync(full, "utf8").slice(0, 20000) });
      }
    }
  }

  search(query: string, limit = 8): MemoryHit[] {
    return this.docs
      .map((doc) => ({ score: score(query, doc.text), path: doc.path, snippet: doc.text.slice(0, 800) }))
      .filter((x) => x.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }
}
