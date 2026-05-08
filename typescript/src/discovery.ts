import type { AdapterSpec, ModuleSpec } from "./core.js";
import * as storage from "./plugins/storage.js";
import * as logger from "./plugins/logger.js";
import * as app from "./plugins/app.js";
import * as aiServiter from "./plugins/aiServiter.js";

type PluginModule = {
  REGISTER_MODULES?: ModuleSpec[];
  REGISTER_ADAPTERS?: AdapterSpec[];
};

export function discover(): { modules: ModuleSpec[]; adapters: AdapterSpec[] } {
  const plugins: PluginModule[] = [storage, logger, app, aiServiter];
  return {
    modules: plugins.flatMap((plugin) => plugin.REGISTER_MODULES ?? []),
    adapters: plugins.flatMap((plugin) => plugin.REGISTER_ADAPTERS ?? []),
  };
}
