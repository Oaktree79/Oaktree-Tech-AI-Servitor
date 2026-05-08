from lattice import AdapterSpec, Capability, ModuleSpec


def start_app(ctx):
    storage = ctx.resolve("storage", (2, 0))
    logger = ctx.resolve("logger", (1, 0))

    class App:
        def run(self):
            logger.info("app starting")
            storage.put("hello", "world")
            logger.info(f"read back: {storage.get('hello')}")
            storage.put_json("obj", {"ready": True})
            logger.info(f"json-capable: {bool(storage.get('obj'))}")

    ctx.bind(Capability("app", (1, 0)), App())


def build_storage_v2(ctx):
    v1 = ctx.resolve("storage", (1, 0))

    class StorageV2:
        def put(self, key, value):
            return v1.put(key, value)

        def get(self, key):
            return v1.get(key)

        def put_json(self, key, obj):
            import json
            return v1.put(key, json.dumps(obj))

    return StorageV2()


REGISTER_MODULES = [
    ModuleSpec(
        name="app",
        provides=[Capability("app", (1, 0))],
        requires=[Capability("storage", (2, 0)), Capability("logger", (1, 0))],
        start=start_app,
    )
]

REGISTER_ADAPTERS = [
    AdapterSpec(
        src=Capability("storage", (1, 0)),
        dst=Capability("storage", (2, 0)),
        build=build_storage_v2,
    )
]
