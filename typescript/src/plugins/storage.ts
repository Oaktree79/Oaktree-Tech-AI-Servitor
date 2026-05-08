import type { ModuleSpec } from "../core.js";

export const REGISTER_MODULES: ModuleSpec[] = [
  {
    name: "storage-v1",
    provides: [{ name: "storage", version: [1, 0], traits: ["memory"] }],
    requires: [],
    start(ctx) {
      const data = new Map<string, unknown>();
      ctx.bind({ name: "storage", version: [1, 0], traits: ["memory"] }, {
        put(key: string, value: unknown) {
          console.log(`[storage-v1] put ${key}=${JSON.stringify(value)}`);
          data.set(key, value);
        },
        get(key: string) {
          console.log(`[storage-v1] get ${key}`);
          return data.get(key);
        },
      });
    },
  },
];

export const REGISTER_ADAPTERS = [];
