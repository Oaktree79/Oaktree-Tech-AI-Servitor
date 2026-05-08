from __future__ import annotations

import argparse
import json

from .deployment_validator import DeploymentValidator
from .real_llm_workflow import RealLLMWorkflowHarness
from .defaults_scanner import DefaultsScanner
from .security_review import SecurityReviewToolkit
from .full_workflow_runner import FullWorkflowRunner
from .monitoring_backup_validator import MonitoringBackupValidator


def main():
    parser = argparse.ArgumentParser(description="AI Serviter final validation CLI")
    parser.add_argument("--root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("deployment-check")
    sub.add_parser("llm-workflow-check")
    sub.add_parser("defaults-scan")
    sub.add_parser("security-review")

    workflow = sub.add_parser("full-workflow")
    workflow.add_argument("instruction")

    sub.add_parser("metrics-check")
    backup = sub.add_parser("backup-create")
    backup.add_argument("--out", default="backups")

    args = parser.parse_args()

    if args.command == "deployment-check":
        validator = DeploymentValidator(args.root)
        print(json.dumps({
            "files": validator.validate_files_present(),
            "docker_compose": validator.docker_compose_config(),
            "kubernetes": validator.kubernetes_dry_run(),
        }, indent=2))
    elif args.command == "llm-workflow-check":
        print(json.dumps(RealLLMWorkflowHarness(args.root).validate_patch_generation(auto_apply=False), indent=2))
    elif args.command == "defaults-scan":
        scanner = DefaultsScanner(args.root)
        print(json.dumps({"files": scanner.scan_files(), "environment": scanner.scan_environment()}, indent=2))
    elif args.command == "security-review":
        print(json.dumps(SecurityReviewToolkit(args.root).run(), indent=2))
    elif args.command == "full-workflow":
        print(json.dumps(FullWorkflowRunner(args.root).run(args.instruction), indent=2))
    elif args.command == "metrics-check":
        print(json.dumps(MonitoringBackupValidator(args.root).validate_metrics(), indent=2))
    elif args.command == "backup-create":
        print(json.dumps(MonitoringBackupValidator(args.root).create_backup(args.out), indent=2))


if __name__ == "__main__":
    main()
