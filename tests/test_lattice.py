import pytest

from lattice import AdapterSpec, Capability, Kernel, ModuleSpec


def test_adapter_bridges_capability_version():
    events = []

    def start_storage(ctx):
        class StorageV1:
            def put(self, key, value):
                events.append(("put", key, value))

        ctx.bind(Capability("storage", (1, 0)), StorageV1())

    def build_storage_v2(ctx):
        v1 = ctx.resolve("storage", (1, 0))

        class StorageV2:
            def put_json(self, key, obj):
                return v1.put(key, obj)

        return StorageV2()

    def start_app(ctx):
        storage = ctx.resolve("storage", (2, 0))
        storage.put_json("x", {"ok": True})

    kernel = Kernel(
        modules=[
            ModuleSpec("storage", [Capability("storage", (1, 0))], [], start_storage),
            ModuleSpec("app", [Capability("app", (1, 0))], [Capability("storage", (2, 0))], start_app),
        ],
        adapters=[
            AdapterSpec(Capability("storage", (1, 0)), Capability("storage", (2, 0)), build_storage_v2)
        ],
    )

    kernel.start()
    assert events == [("put", "x", {"ok": True})]


def test_missing_dependency_raises():
    kernel = Kernel(
        modules=[
            ModuleSpec(
                "app",
                [Capability("app", (1, 0))],
                [Capability("database", (1, 0))],
                lambda ctx: None,
            )
        ]
    )

    with pytest.raises(RuntimeError):
        kernel.start()


def test_traits_filter_provider():
    def start_storage(ctx):
        ctx.bind(Capability("storage", (1, 0), frozenset({"memory"})), object())

    kernel = Kernel(
        modules=[
            ModuleSpec(
                "storage",
                [Capability("storage", (1, 0), frozenset({"memory"}))],
                [],
                start_storage,
            )
        ]
    )

    kernel.start()
    assert kernel.ctx.resolve("storage", (1, 0), frozenset({"memory"}))
