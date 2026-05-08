import importlib
import sys
import time
from pathlib import Path

from .discovery import discover


class HotReloadManager:
    def __init__(self, kernel, plugin_package: str, plugin_dir: str):
        self.kernel = kernel
        self.plugin_package = plugin_package
        self.plugin_dir = Path(plugin_dir)
        self._mtimes = {}

    def snapshot(self):
        self._mtimes = {
            path: path.stat().st_mtime
            for path in self.plugin_dir.glob("*.py")
            if path.name != "__init__.py"
        }

    def changed(self) -> bool:
        current = {
            path: path.stat().st_mtime
            for path in self.plugin_dir.glob("*.py")
            if path.name != "__init__.py"
        }
        return current != self._mtimes

    def reload_once_if_changed(self) -> bool:
        if not self.changed():
            return False

        prefix = self.plugin_package + "."
        for name in list(sys.modules):
            if name.startswith(prefix):
                importlib.reload(sys.modules[name])

        modules, adapters = discover(self.plugin_package)
        self.kernel.restart(modules, adapters)
        self.snapshot()
        return True

    def watch(self, interval_seconds: float = 1.0):
        self.snapshot()
        print("[hot-reload] watching plugin changes. Press Ctrl+C to stop.")
        try:
            while True:
                if self.reload_once_if_changed():
                    print("[hot-reload] plugins reloaded")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("[hot-reload] stopped")
