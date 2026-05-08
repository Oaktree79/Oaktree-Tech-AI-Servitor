import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, extname } from "node:path";

export type FileNode = {
  path: string;
  kind: "file" | "directory";
  extension: string;
  sizeBytes: number;
  depth: number;
  sha256?: string;
  lineCount?: number;
  language?: string;
};

const ignoreDirs = new Set([".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"]);

function languageFor(path: string): string | undefined {
  const map: Record<string, string> = {
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".py": "python",
    ".json": "json",
    ".md": "markdown",
  };
  return map[extname(path).toLowerCase()];
}

export class FileSystemMatrix {
  public nodes: FileNode[] = [];

  constructor(public root: string) {}

  scan(): this {
    this.nodes = [];
    this.walk(this.root);
    return this;
  }

  private walk(current: string): void {
    for (const entry of readdirSync(current)) {
      if (ignoreDirs.has(entry)) continue;
      const full = join(current, entry);
      const stat = statSync(full);
      const rel = relative(this.root, full);
      const depth = rel.split(/[\\/]/).length - 1;

      if (stat.isDirectory()) {
        this.nodes.push({ path: rel, kind: "directory", extension: "", sizeBytes: 0, depth });
        this.walk(full);
      } else {
        const buffer = readFileSync(full);
        const text = buffer.toString("utf8");
        this.nodes.push({
          path: rel,
          kind: "file",
          extension: extname(full),
          sizeBytes: stat.size,
          depth,
          sha256: createHash("sha256").update(buffer).digest("hex"),
          lineCount: text.split(/\r?\n/).length,
          language: languageFor(full),
        });
      }
    }
  }

  summary() {
    const files = this.nodes.filter((n) => n.kind === "file");
    const dirs = this.nodes.filter((n) => n.kind === "directory");
    const languages: Record<string, number> = {};
    for (const node of files) {
      if (node.language) languages[node.language] = (languages[node.language] ?? 0) + 1;
    }
    return {
      root: this.root,
      files: files.length,
      directories: dirs.length,
      totalSizeBytes: files.reduce((sum, f) => sum + f.sizeBytes, 0),
      languages,
    };
  }
}
