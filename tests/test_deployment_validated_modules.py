from ai_serviter.integration_harness import IntegrationHarness
from ai_serviter.deployment_validator import DeploymentValidator
from ai_serviter.llm_validation import LLMConfigValidator
from ai_serviter.security_hardening import SecurityHardeningChecker
from ai_serviter.postgres_config import ProductionDatabaseConfig
from ai_serviter.user_management import UserManagement
from ai_serviter.database import ServiterDatabase


def test_integration_harness_smoke(tmp_path):
    (tmp_path / "demo.py").write_text("print('ok')\n", encoding="utf-8")
    result = IntegrationHarness(tmp_path).run_smoke()
    assert "ok" in result


def test_deployment_validator_files_present_shape(tmp_path):
    validator = DeploymentValidator(tmp_path)
    result = validator.validate_files_present()
    assert "missing" in result


def test_llm_validator_status():
    result = LLMConfigValidator().validate_status()
    assert "ready_for_real_edits" in result


def test_security_hardening_checker(tmp_path):
    result = SecurityHardeningChecker(tmp_path).check()
    assert "checks" in result


def test_postgres_config_validation():
    result = ProductionDatabaseConfig().validate()
    assert "missing" in result


def test_user_management(tmp_path):
    db = ServiterDatabase(tmp_path / "s.db")
    users = UserManagement(db)
    users.create_user("bob", "password", "operator")
    assert any(u["username"] == "bob" for u in users.list_users())
    users.set_role("bob", "admin")
    assert any(u["role"] == "admin" for u in users.list_users())
    users.delete_user("bob")
    assert not any(u["username"] == "bob" for u in users.list_users())
