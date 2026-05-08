from ai_serviter import (
    ClosedLoopCodingAgent,
    DockerSandbox,
    GitIntegration,
    OverrideControls,
    PolicyEngine,
    RBAC,
    SelfCorrectionLoop,
    ServiterDatabase,
    ServiterRuntime,
    StructuredPatchParser,
)


def test_structured_patch_parser():
    parser = StructuredPatchParser()
    patch = parser.parse('{"summary":"x","edits":[{"path":"a.txt","after":"hello"}],"test_command":["python","-V"]}')
    assert patch.edits[0].path == "a.txt"


def test_policy_blocks_env():
    policy = PolicyEngine(".")
    decision = policy.evaluate_edits("modify code", [type("E", (), {"path": ".env"})()], auto_apply=True)
    assert not decision["allowed"]


def test_closed_loop_dry_run_no_edits(tmp_path):
    agent = ClosedLoopCodingAgent(tmp_path)
    result = agent.run("create hello file", auto_apply=False)
    assert result["status"] in {"failed", "no_edits_proposed"}


def test_docker_sandbox_available_returns_bool(tmp_path):
    assert isinstance(DockerSandbox(tmp_path).available(), bool)


def test_rbac():
    assert RBAC().allowed("admin", "system:override")
    assert not RBAC().allowed("viewer", "system:override")


def test_override_pause_runtime(tmp_path):
    db = ServiterDatabase(tmp_path / "s.db")
    controls = OverrideControls(db, tmp_path)
    controls.pause("testing")
    assert controls.is_paused()
    controls.resume()
    assert not controls.is_paused()


def test_runtime_paused(tmp_path):
    runtime = ServiterRuntime(tmp_path)
    runtime.overrides.pause("testing")
    assert runtime.run_once()["status"] == "paused"


def test_git_integration_status_shape(tmp_path):
    git = GitIntegration(tmp_path)
    result = git.status()
    assert "returncode" in result


def test_self_correction_dry_run(tmp_path):
    loop = SelfCorrectionLoop(tmp_path)
    result = loop.repair("fix tests", {"error": "x"})
    assert "status" in result
