from lattice import Capability, ModuleSpec


def start_logger(ctx):
    class LoggerV1:
        def info(self, msg):
            print(f"[info] {msg}")

        def warn(self, msg):
            print(f"[warn] {msg}")

        def error(self, msg):
            print(f"[error] {msg}")

    ctx.bind(Capability("logger", (1, 0)), LoggerV1())


REGISTER_MODULES = [
    ModuleSpec(
        name="logger",
        provides=[Capability("logger", (1, 0))],
        requires=[],
        start=start_logger,
    )
]

REGISTER_ADAPTERS = []
