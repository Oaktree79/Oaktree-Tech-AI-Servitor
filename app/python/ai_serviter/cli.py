from __future__ import annotations

import argparse
import json

from .iso_packager import ISOPackager
from .runtime import ServiterRuntime
from .serviter import AIServiter


def main():
    parser = argparse.ArgumentParser(description="AI Serviter coding module")
    parser.add_argument("root", nargs="?", default=".", help="Project root to analyze")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("analyze")

    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("request")

    propose_parser = sub.add_parser("propose")
    propose_parser.add_argument("request")

    export_parser = sub.add_parser("export-matrix")
    export_parser.add_argument("--out", default=".serviter")

    search_parser = sub.add_parser("search-memory")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=8)

    submit_parser = sub.add_parser("submit")
    submit_parser.add_argument("instruction")
    submit_parser.add_argument("--priority", type=int, default=100)

    approve_parser = sub.add_parser("approve")
    approve_parser.add_argument("task_id")

    reject_parser = sub.add_parser("reject")
    reject_parser.add_argument("task_id")

    sub.add_parser("run-once")
    sub.add_parser("tasks")

    iso_tree_parser = sub.add_parser("create-iso-tree")
    iso_tree_parser.add_argument("--out", default="AI_SERVITER_ISO")
    iso_tree_parser.add_argument("--name", default="AI Serviter")

    iso_parser = sub.add_parser("build-iso")
    iso_parser.add_argument("--tree", default="AI_SERVITER_ISO")
    iso_parser.add_argument("--out", default="AI_SERVITER.iso")
    iso_parser.add_argument("--label", default="AI_SERVITER")

    args = parser.parse_args()

    if args.command in {"submit", "approve", "reject", "run-once", "tasks"}:
        runtime = ServiterRuntime(args.root)
        if args.command == "submit":
            print(json.dumps(runtime.submit(args.instruction, args.priority).__dict__, indent=2))
        elif args.command == "approve":
            runtime.approvals.approve(args.task_id)
            print(json.dumps(runtime.queue.get(args.task_id).__dict__, indent=2))
        elif args.command == "reject":
            runtime.approvals.reject(args.task_id)
            print(json.dumps(runtime.queue.get(args.task_id).__dict__, indent=2))
        elif args.command == "run-once":
            print(json.dumps(runtime.run_once(), indent=2))
        elif args.command == "tasks":
            print(json.dumps([t.__dict__ for t in runtime.queue.list()], indent=2))
        return

    if args.command in {"create-iso-tree", "build-iso"}:
        packager = ISOPackager(args.root)
        if args.command == "create-iso-tree":
            path = packager.create_iso_tree(args.out, args.name)
            print(json.dumps({"iso_tree": str(path)}, indent=2))
        else:
            result = packager.build_iso(args.tree, args.out, args.label)
            print(json.dumps(result.to_dict(), indent=2))
        return

    serviter = AIServiter(args.root)

    if args.command == "analyze":
        print(json.dumps(serviter.analyze(), indent=2))
    elif args.command == "plan":
        print(json.dumps(serviter.plan(args.request), indent=2))
    elif args.command == "propose":
        print(json.dumps(serviter.propose(args.request), indent=2))
    elif args.command == "export-matrix":
        print(json.dumps(serviter.export_development_matrix(args.out), indent=2))
    elif args.command == "search-memory":
        serviter.memory.build_from_files()
        print(json.dumps(serviter.memory.search(args.query, args.limit), indent=2))


if __name__ == "__main__":
    main()
