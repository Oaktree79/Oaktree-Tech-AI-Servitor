from ai_serviter.llm_runtime import LLMRuntime
from ai_serviter.isolation_manager import IsolationManager
from ai_serviter.pr_automation import PullRequestAutomation
from ai_serviter.secrets_manager import SecretsManager
from ai_serviter.k8s_tester import KubernetesDeploymentTester
from ai_serviter.distributed_worker import DistributedWorker
from ai_serviter.observability import MetricsRegistry
from ai_serviter.oidc_auth import OIDCAuthConfig
from ai_serviter.network_policy import NetworkPolicy


def test_llm_runtime_status():
    status = LLMRuntime().status()
    assert "provider" in status


def test_isolation_status(tmp_path):
    status = IsolationManager(tmp_path).status()
    assert status["local_sandbox_available"] is True


def test_pr_automation_missing_cli(tmp_path):
    result = PullRequestAutomation(tmp_path).create_github_pr("test")
    assert "returncode" in result


def test_secrets_file_backend(tmp_path):
    mgr = SecretsManager("file", tmp_path / "s.json")
    mgr.set_dev_secret("X", "y")
    assert mgr.get("X") == "y"


def test_k8s_status(tmp_path):
    status = KubernetesDeploymentTester(tmp_path).status()
    assert "kubectl_available" in status


def test_distributed_worker_heartbeat(tmp_path):
    worker = DistributedWorker(tmp_path)
    hb = worker.heartbeat()
    assert hb["worker_id"]


def test_metrics_registry():
    m = MetricsRegistry()
    m.inc("x")
    assert "x 1" in m.prometheus()


def test_oidc_status():
    assert "configured" in OIDCAuthConfig().ready()


def test_network_policy_blocks_metadata():
    decision = NetworkPolicy().check_url("http://169.254.169.254/latest/meta-data")
    assert decision["allowed"] is False


def test_network_policy_allows_github():
    decision = NetworkPolicy().check_url("https://github.com/example/repo")
    assert decision["allowed"] is True
