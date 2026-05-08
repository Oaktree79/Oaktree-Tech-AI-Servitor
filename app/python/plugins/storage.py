from lattice import Capability, ModuleSpec


def start_storage(ctx):
    class StorageV1:
        def __init__(self):
            self._data = {}

        def put(self, key, value):
            print(f"[storage-v1] put {key}={value}")
            self._data[key] = value

        def get(self, key):
            print(f"[storage-v1] get {key}")
            return self._data.get(key)

    ctx.bind(Capability("storage", (1, 0), frozenset({"memory"})), StorageV1())


REGISTER_MODULES = [
    ModuleSpec(
        name="storage-v1",
        provides=[Capability("storage", (1, 0), frozenset({"memory"}))],
        requires=[],
        start=start_storage,
    )
]

REGISTER_ADAPTERS = []
