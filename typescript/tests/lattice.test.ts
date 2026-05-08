import test from "node:test";
import assert from "node:assert/strict";
import { Kernel, type AdapterSpec, type ModuleSpec } from "../src/core.js";

test("adapter bridges capability version", async () => {
  const events: unknown[] = [];

  const modules: ModuleSpec[] = [
    {
      name: "storage",
      provides: [{ name: "storage", version: [1, 0] }],
      requires: [],
      start(ctx) {
        ctx.bind({ name: "storage", version: [1, 0] }, {
          put(key: string, value: unknown) {
            events.push(["put", key, value]);
          },
        });
      },
    },
    {
      name: "app",
      provides: [{ name: "app", version: [1, 0] }],
      requires: [{ name: "storage", version: [2, 0] }],
      start(ctx) {
        const storage = ctx.resolve<{ putJson(key: string, value: unknown): void }>("storage", [2, 0]);
        storage.putJson("x", { ok: true });
      },
    },
  ];

  const adapters: AdapterSpec[] = [
    {
      src: { name: "storage", version: [1, 0] },
      dst: { name: "storage", version: [2, 0] },
      build(ctx) {
        const v1 = ctx.resolve<{ put(key: string, value: unknown): void }>("storage", [1, 0]);
        return {
          putJson(key: string, value: unknown) {
            v1.put(key, value);
          },
        };
      },
    },
  ];

  const kernel = new Kernel(modules, adapters);
  await kernel.start();

  assert.deepEqual(events, [["put", "x", { ok: true }]]);
});
