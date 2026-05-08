import test from "node:test";
import assert from "node:assert/strict";
import { AIServiter } from "../src/serviter/serviter.js";

test("AI Serviter analyzes and plans", () => {
  const serviter = new AIServiter(".");
  const analysis = serviter.analyze();
  assert.ok(analysis.matrix.files > 0);

  const plan = serviter.plan("add plugin module test");
  assert.equal(plan.task.testCommand, "npm test");
});
