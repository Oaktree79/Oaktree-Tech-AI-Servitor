import type { ModuleSpec } from "../core.js";
import { AIServiter } from "../serviter/serviter.js";

export const REGISTER_MODULES: ModuleSpec[] = [
  {
    name: "ai-serviter",
    provides: [{ name: "ai_serviter", version: [1, 0] }],
    requires: [],
    start(ctx) {
      const root = (ctx.config.projectRoot as string | undefined) ?? ".";
      ctx.bind({ name: "ai_serviter", version: [1, 0] }, new AIServiter(root));
    },
  },
];

export const REGISTER_ADAPTERS = [];
