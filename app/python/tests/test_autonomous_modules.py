from ai_serviter import (
    ApprovalManager,
    ApprovalPolicy,
    AuthManager,
    AutoPatcher,
    ServiterDatabase,
    ServiterRuntime,
    TaskQueue,
    TestRunner,
    ToolSandbox,
)


def test_task_queue_and_state_machine(tmp_path):
    db = ServiterDatabase(tmp_path / "s.db")
    queue = TaskQueue(db)
    task = queue.submit("analyze project", requires_approval=False)
    assert task.status == "queued"
    queue.transition(task.id, "running")
    queue.transition(task.id, "succeeded", result={"ok": True})
    assert queue.get(task.id).result == {"ok": True}


def test_approval_manager(tmp_path):
    db = ServiterDatabase(tmp_path / "s.db")
    queue = TaskQueue(db)
    mgr = ApprovalManager(db, queue)
    task = queue.submit("apply patch", requires_approval=True)
    mgr.approve(task.id)
    assert queue.get(task.id).status == "approved"


def test_approval_policy():
    policy = ApprovalPolicy()
    assert policy.requires_approval("apply patch to file")
    assert not policy.requires_approval("analyze project")


def test_auth_manager(tmp_path):
    db = ServiterDatabase(tmp_path / "s.db")
    auth = AuthManager(db, secret="test")
    auth.create_user("alice", "password", "admin")
    user = auth.authenticate("alice", "password")
    assert user and user.role == "admin"
    token = auth.issue_token(user)
    assert auth.verify_token(token).username == "alice"


def test_sandbox_allowed_command(tmp_path):
    sandbox = ToolSandbox(tmp_path, allowed_commands={"python"}, timeout_seconds=10)
    result = sandbox.run(["python", "-c", "print('ok')"])
    assert result.returncode == 0
    assert "ok" in result.stdout


def test_test_runner_detects_compile(tmp_path):
    (tmp_path / "x.py").write_text("print('ok')\n", encoding="utf-8")
    runner = TestRunner(tmp_path)
    result = runner.run(["python", "-m", "compileall", "-q", "."])
    assert result["returncode"] == 0


def test_auto_patcher_proposes(tmp_path):
    patcher = AutoPatcher(tmp_path)
    result = patcher.propose_patch("create file", {"files": []})
    assert result["provider"] == "dry-run"


def test_runtime_submit_and_run(tmp_path):
    (tmp_path / "demo.py").write_text("print('demo')\n", encoding="utf-8")
    runtime = ServiterRuntime(tmp_path)
    task = runtime.submit("analyze project")
    result = runtime.run_once()
    assert result["status"] == "succeeded"
