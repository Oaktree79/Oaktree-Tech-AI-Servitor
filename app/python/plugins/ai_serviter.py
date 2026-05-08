from lattice import Capability, ModuleSpec
from ai_serviter import AIServiter


def start_ai_serviter(ctx):
    root = ctx.config.get("project_root", ".")
    ctx.bind(Capability("ai_serviter", (1, 0)), AIServiter(root, config=ctx.config))


REGISTER_MODULES = [
    ModuleSpec(
        name="ai-serviter",
        provides=[Capability("ai_serviter", (1, 0))],
        requires=[],
        start=start_ai_serviter,
    )
]

REGISTER_ADAPTERS = []
