import importlib
import pkgutil

def discover(entry_package: str):
    modules = []
    adapters = []
    package = importlib.import_module(entry_package)

    for info in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        imported = importlib.import_module(info.name)
        modules.extend(getattr(imported, "REGISTER_MODULES", []))
        adapters.extend(getattr(imported, "REGISTER_ADAPTERS", []))

    return modules, adapters
