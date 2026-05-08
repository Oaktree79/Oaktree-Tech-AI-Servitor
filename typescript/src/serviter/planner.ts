import type { SymbolRecord } from "./codeIndex.js";

export type CodingTask = {
  title: string;
  goal: string;
  filesToInspect: string[];
  filesToModify: string[];
  testCommand: string;
  riskLevel: "low" | "medium" | "high";
  steps: string[];
};

export class CodingTaskPlanner {
  plan(request: string, matrixSummary: Record<string, unknown>, hits: SymbolRecord[]): CodingTask {
    const lower = request.toLowerCase();
    let riskLevel: CodingTask["riskLevel"] = "medium";
    if (/(security|auth|payment|database|delete)/.test(lower)) riskLevel = "high";
    if (/(readme|docs|comment)/.test(lower)) riskLevel = "low";

    const filesToInspect = [...new Set(hits.map((h) => h.path))].slice(0, 10);
    const filesToModify = lower.includes("test")
      ? ["tests/"]
      : lower.includes("plugin") || lower.includes("module")
        ? ["src/plugins/"]
        : filesToInspect.slice(0, 3);

    return {
      title: request.trim().slice(0, 80) || "Untitled coding task",
      goal: request,
      filesToInspect,
      filesToModify: filesToModify.length ? filesToModify : ["<new-file-to-be-created>"],
      testCommand: "npm test",
      riskLevel,
      steps: [
        "Scan filesystem matrix.",
        "Inspect matching symbols and nearby tests.",
        "Create minimal patch.",
        "Run formatter, static checks, and tests.",
        "Run security scan before finalizing.",
      ],
    };
  }
}
