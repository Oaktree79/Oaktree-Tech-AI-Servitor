from ai_serviter.path_resolver import ProjectRootResolver
from ai_serviter.real_llm_workflow import RealLLMWorkflowHarness
from ai_serviter.defaults_scanner import DefaultsScanner
from ai_serviter.security_review import SecurityReviewToolkit
from ai_serviter.full_workflow_runner import FullWorkflowRunner
from ai_serviter.monitoring_backup_validator import MonitoringBackupValidator


def test_project_root_resolver(tmp_path):
    (tmp_path / "python").mkdir()
    (tmp_path / "deploy").mkdir()
    assert ProjectRootResolver(tmp_path / "python").resolve() == tmp_path


def test_real_llm_parser_contract(tmp_path):
    result = RealLLMWorkflowHarness(tmp_path).validate_parser_contract()
    assert result["ok"]


def test_defaults_scanner(tmp_path):
    (tmp_path / "x.txt").write_text("password=change-me\n", encoding="utf-8")
    result = DefaultsScanner(tmp_path).scan_files()
    assert not result["ok"]


def test_security_review_shape(tmp_path):
    result = SecurityReviewToolkit(tmp_path).run()
    assert "hardening" in result


def test_full_workflow_runner(tmp_path):
    (tmp_path / "demo.py").write_text("print('ok')\n", encoding="utf-8")
    result = FullWorkflowRunner(tmp_path).run("analyze project")
    assert "worker" in result


def test_monitoring_backup_validator(tmp_path):
    validator = MonitoringBackupValidator(tmp_path)
    metrics = validator.validate_metrics()
    assert metrics["ok"]
    backup = validator.create_backup()
    assert backup["ok"]
    readable = validator.validate_backup_readable(backup["backup"])
    assert readable["ok"]
