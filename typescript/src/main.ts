import { Kernel } from "./core.js";
import { discover } from "./discovery.js";
import type { AIServiter } from "./serviter/serviter.js";

type App = {
  run(): void;
};

const { modules, adapters } = discover();
const kernel = new Kernel(modules, adapters);

await kernel.start({ projectRoot: "." });

const app = kernel.ctx.resolve<App>("app", [1, 0]);
app.run();

const serviter = kernel.ctx.resolve<AIServiter>("ai_serviter", [1, 0]);
console.log("[ai-serviter] summary:", serviter.analyze());

await kernel.stop();
