from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Capability:
    name: str
    version: Tuple[int, ...]
    traits: frozenset[str] = frozenset()

    def compatible_with(self, provider: "Capability") -> bool:
        return (
            self.name == provider.name
            and provider.version >= self.version
            and provider.traits.issuperset(self.traits)
        )


@dataclass
class ModuleSpec:
    name: str
    provides: List[Capability]
    requires: List[Capability]
    start: Callable[["Context"], None]
    stop: Callable[["Context"], None] = lambda ctx: None


@dataclass
class AdapterSpec:
    src: Capability
    dst: Capability
    build: Callable[["Context"], Any]


class Context:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._bindings: Dict[Capability, Any] = {}

    def bind(self, cap: Capability, value: Any):
        self._bindings[cap] = value

    def resolve(
        self,
        name: str,
        min_version: Tuple[int, ...] = (0,),
        traits: frozenset[str] = frozenset(),
    ) -> Any:
        need = Capability(name=name, version=min_version, traits=traits)
        candidates = [cap for cap in self._bindings if need.compatible_with(cap)]
        if not candidates:
            raise KeyError(f"No binding for capability {name} >= {min_version}")
        best = max(candidates, key=lambda c: c.version)
        return self._bindings[best]

    def list_bindings(self) -> List[Capability]:
        return sorted(self._bindings.keys(), key=lambda c: (c.name, c.version))


class Kernel:
    def __init__(self, modules: Iterable[ModuleSpec], adapters: Iterable[AdapterSpec] = ()):
        self.modules = list(modules)
        self.adapters = list(adapters)
        self.ctx = Context()
        self._started: List[ModuleSpec] = []

    def _find_provider(self, need: Capability) -> Optional[Capability]:
        for have in self.ctx.list_bindings():
            if need.compatible_with(have):
                return have
        return None

    def _try_adapt(self, need: Capability) -> Optional[Capability]:
        for adapter in self.adapters:
            if not need.compatible_with(adapter.dst):
                continue
            for bound in self.ctx.list_bindings():
                if adapter.src.compatible_with(bound):
                    built = adapter.build(self.ctx)
                    self.ctx.bind(adapter.dst, built)
                    return adapter.dst
        return None

    def _requirements_satisfied_runtime(self, module: ModuleSpec) -> bool:
        for requirement in module.requires:
            if not self._find_provider(requirement) and not self._try_adapt(requirement):
                return False
        return True

    def _cap_available(self, need: Capability, available: List[Capability]) -> bool:
        if any(need.compatible_with(have) for have in available):
            return True
        for adapter in self.adapters:
            if need.compatible_with(adapter.dst) and any(adapter.src.compatible_with(have) for have in available):
                return True
        return False

    def _requirements_satisfied_for_ordering(self, module: ModuleSpec, available: List[Capability]) -> bool:
        return all(self._cap_available(req, available) for req in module.requires)

    def _toposort_start_order(self) -> List[ModuleSpec]:
        pending = list(self.modules)
        order: List[ModuleSpec] = []
        available: List[Capability] = []

        changed = True
        while pending and changed:
            changed = False
            for module in pending[:]:
                if self._requirements_satisfied_for_ordering(module, available):
                    order.append(module)
                    pending.remove(module)
                    available.extend(module.provides)
                    # Adapter outputs become available for downstream ordering once source is available.
                    adapter_added = True
                    while adapter_added:
                        adapter_added = False
                        for adapter in self.adapters:
                            if any(adapter.src.compatible_with(have) for have in available):
                                if not any(adapter.dst.compatible_with(have) or have.compatible_with(adapter.dst) for have in available):
                                    available.append(adapter.dst)
                                    adapter_added = True
                    changed = True

        if pending:
            missing = {
                module.name: [req for req in module.requires if not self._cap_available(req, available)]
                for module in pending
            }
            raise RuntimeError(f"Unresolvable modules: {missing}")

        return order

    def start(self, config: Optional[Dict[str, Any]] = None):
        if config:
            self.ctx.config.update(config)
        for module in self._toposort_start_order():
            if not self._requirements_satisfied_runtime(module):
                raise RuntimeError(f"Runtime requirements unsatisfied for module {module.name}")
            module.start(self.ctx)
            self._started.append(module)

    def stop(self):
        for module in reversed(self._started):
            try:
                module.stop(self.ctx)
            except Exception as exc:
                print(f"[kernel] error stopping {module.name}: {exc}")
        self._started.clear()

    def restart(self, modules: Iterable[ModuleSpec], adapters: Iterable[AdapterSpec] = ()):
        old_config = dict(self.ctx.config)
        self.stop()
        self.modules = list(modules)
        self.adapters = list(adapters)
        self.ctx = Context(old_config)
        self.start()
