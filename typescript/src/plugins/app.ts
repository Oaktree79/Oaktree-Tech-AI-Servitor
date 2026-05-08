import type { AdapterSpec, Context, ModuleSpec } from "../core.js";

type StorageV1 = {
  put(key: string, value: unknown): void;
  get(key: string): unknown;
};

type StorageV2 = StorageV1 & {
  putJson(key: string, value: unknown): void;
};

type Logger = {
  info(message: string): void;
};

export const REGISTER_MODULES: ModuleSpec[] = [
  {
    name: "app",
    provides: [{ name: "app", version: [1, 0] }],
    requires: [
      { name: "storage", version: [2, 0] },
      { name: "logger", version: [1, 0] },
    ],
    start(ctx) {
      const storage = ctx.resolve<StorageV2>("storage", [2, 0]);
      const logger = ctx.resolve<Logger>("logger", [1, 0]);

      ctx.bind({ name: "app", version: [1, 0] }, {
        run() {
          logger.info("app starting");
          storage.put("hello", "world");
          logger.info(`read back: ${storage.get("hello")}`);
          storage.putJson("obj", { ready: true });
          logger.info(`json-capable: ${Boolean(storage.get("obj"))}`);
        },
      });
    },
  },
];

function buildStorageV2(ctx: Context): StorageV2 {
  const v1 = ctx.resolve<StorageV1>("storage", [1, 0]);
  return {
    put: (key, value) => v1.put(key, value),
    get: (key) => v1.get(key),
    putJson: (key, value) => v1.put(key, JSON.stringify(value)),
  };
}

export const REGISTER_ADAPTERS: AdapterSpec[] = [
  {
    src: { name: "storage", version: [1, 0] },
    dst: { name: "storage", version: [2, 0] },
    build: buildStorageV2,
  },
];
