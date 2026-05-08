import type { ModuleSpec } from "../core.js";

export const REGISTER_MODULES: ModuleSpec[] = [
  {
    name: "logger",
    provides: [{ name: "logger", version: [1, 0] }],
    requires: [],
    start(ctx) {
      ctx.bind({ name: "logger", version: [1, 0] }, {
        info(message: string) {
          console.log(`[info] ${message}`);
        },
        warn(message: string) {
          console.log(`[warn] ${message}`);
        },
        error(message: string) {
          console.log(`[error] ${message}`);
        },
      });
    },
  },
];

export const REGISTER_ADAPTERS = [];
