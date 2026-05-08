import { Kernel } from "./core.js";
import { discover } from "./discovery.js";

console.log("Use nodemon, tsx watch, or your runtime watcher to restart on file changes.");

const { modules, adapters } = discover();
const kernel = new Kernel(modules, adapters);
await kernel.start();
kernel.ctx.resolve<{ run(): void }>("app", [1, 0]).run();
await kernel.stop();
