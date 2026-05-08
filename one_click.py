from __future__ import annotations

import argparse
import json

from .config_wizard import ConfigWizard
from .environment_setup import EnvironmentSetup
from .launcher import AutoLauncher
from .service_registration import ServiceRegistrar
from .crash_reporter import CrashReporter


def setup(root: str):
    try:
        env = EnvironmentSetup(root).prepare()
        config = ConfigWizard(root).create()
        services = ServiceRegistrar(root).generate()
        return {"ok": True, "environment": env, "config": config, "services": services}
    except Exception as exc:
        crash = CrashReporter(root).report_exception(exc, {"phase": "setup"})
        return {"ok": False, "error": str(exc), "crash": crash}


def launch(root: str):
    try:
        return {"ok": True, "launch": AutoLauncher(root).launch_all()}
    except Exception as exc:
        crash = CrashReporter(root).report_exception(exc, {"phase": "launch"})
        return {"ok": False, "error": str(exc), "crash": crash}


def main():
    parser = argparse.ArgumentParser(description="AI Serviter one-click setup")
    parser.add_argument("--root", default=".")
    parser.add_argument("command", choices=["setup", "launch", "service-files", "secrets"])
    args = parser.parse_args()

    if args.command == "setup":
        print(json.dumps(setup(args.root), indent=2))
    elif args.command == "launch":
        print(json.dumps(launch(args.root), indent=2))
    elif args.command == "service-files":
        print(json.dumps(ServiceRegistrar(args.root).generate(), indent=2))
    elif args.command == "secrets":
        print(json.dumps(ConfigWizard(args.root).generate_secrets(), indent=2))


if __name__ == "__main__":
    main()
