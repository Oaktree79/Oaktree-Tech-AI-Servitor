import { CodeIndex } from "./codeIndex.js";
import { FileSystemMatrix } from "./filesystemMatrix.js";
import { CodingTaskPlanner } from "./planner.js";
import { SecurityScanner } from "./security.js";
import { VectorMemory } from "./memory.js";

export class AIServiter {
  public matrix: FileSystemMatrix;
  public index: CodeIndex;
  public planner = new CodingTaskPlanner();
  public security: SecurityScanner;
  public memory: VectorMemory;

  constructor(public root: string) {
    this.matrix = new FileSystemMatrix(root);
    this.index = new CodeIndex(root);
    this.security = new SecurityScanner(root);
    this.memory = new VectorMemory(root);
  }

  analyze() {
    this.matrix.scan();
    this.index.build();
    this.security.scan();
    this.memory.build();
    return {
      matrix: this.matrix.summary(),
      symbolCount: this.index.symbols.length,
      securityFindings: this.security.findings.length,
      memoryDocuments: this.memory.docs.length,
    };
  }

  plan(request: string) {
    const analysis = this.analyze();
    const hits = this.index.search(request);
    const memoryHits = this.memory.search(request);
    return {
      request,
      analysis,
      symbolHits: hits.slice(0, 25),
      memoryHits,
      securityFindings: this.security.findings.slice(0, 25),
      task: this.planner.plan(request, analysis.matrix, hits),
    };
  }

  propose(request: string) {
    return {
      request,
      plan: this.plan(request),
      proposal: {
        provider: "dry-run",
        text: "Dry-run TypeScript proposal. Connect an external model adapter for generated code.",
      },
    };
  }
}
