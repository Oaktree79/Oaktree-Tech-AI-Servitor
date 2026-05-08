from ai_serviter.config_wizard import ConfigWizard
from ai_serviter.service_registration import ServiceRegistrar
from ai_serviter.updater import AutoUpdater
from ai_serviter.crash_reporter import CrashReporter
from ai_serviter.environment_setup import EnvironmentSetup


def test_config_wizard_generates(tmp_path):
    wizard = ConfigWizard(tmp_path)
    cfg = wizard.create({"port": 9999})
    assert cfg["port"] == 9999
    secrets = wizard.generate_secrets()
    assert "admin_password" in secrets


def test_service_registration_generates(tmp_path):
    result = ServiceRegistrar(tmp_path).generate()
    assert result


def test_updater_no_manifest(tmp_path):
    result = AutoUpdater(tmp_path).check(None)
    assert result["update_available"] is False


def test_crash_reporter(tmp_path):
    reporter = CrashReporter(tmp_path)
    try:
        raise ValueError("boom")
    except Exception as exc:
        result = reporter.report_exception(exc)
    assert result["crash_id"]
    assert reporter.list_reports()


def test_environment_setup_paths(tmp_path):
    setup = EnvironmentSetup(tmp_path)
    result = setup.generate_env()
    assert result["ok"]
