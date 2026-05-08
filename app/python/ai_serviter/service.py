from __future__ import annotations

import argparse
import time

from .api_server import run_api_server
from .observer import FileObserver
from .runtime import ServiterRuntime


def main():
    parser = argparse.ArgumentParser(description="AI Serviter autonomous service runner")
    parser.add_argument("--root", default=".")
    parser.add_argument("--db", default=None)
    parser.add_argument("--mode", choices=["api", "worker", "once", "observer"], default="api")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()

    if args.mode == "api":
        run_api_server(root=args.root, host=args.host, port=args.port, db_path=args.db)
        return

    runtime = ServiterRuntime(root=args.root, db_path=args.db)

    if args.mode == "observer":
        FileObserver(args.root, runtime, args.interval).watch()
        return

    if args.mode == "once":
        print(runtime.run_once())
        return

    print("AI Serviter worker running. Press Ctrl+C to stop.")
    try:
        while True:
            print(runtime.run_once())
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("AI Serviter worker stopped.")


if __name__ == "__main__":
    main()
