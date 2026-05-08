from ai_serviter import AIServiter, FileSystemMatrix, CodeIndex, SecurityScanner


def test_filesystem_matrix_scans_project():
    matrix = FileSystemMatrix(".").scan()
    summary = matrix.summary()
    assert summary["files"] > 0
    assert "root" in summary


def test_code_index_finds_symbols():
    index = CodeIndex(".").build()
    hits = index.search("Kernel")
    assert any(hit.name == "Kernel" for hit in hits)


def test_serviter_plans_task():
    serviter = AIServiter(".")
    plan = serviter.plan("add a plugin module test")
    assert "task" in plan
    assert plan["task"]["test_command"]


def test_security_scanner_runs():
    scanner = SecurityScanner(".").scan()
    assert isinstance(scanner.findings, list)
