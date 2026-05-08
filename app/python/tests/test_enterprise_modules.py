from pathlib import Path

from ai_serviter import AIServiter, DryRunLLMProvider, PatchEngine, SecurityScanner, VectorMemory


def test_dry_run_llm_propose():
    serviter = AIServiter(".", llm=DryRunLLMProvider())
    result = serviter.propose("add a plugin module")
    assert result["proposal"]["provider"] == "dry-run"


def test_patch_engine_apply_and_rollback(tmp_path):
    target = tmp_path / "demo.txt"
    target.write_text("before", encoding="utf-8")

    engine = PatchEngine(tmp_path)
    edit = engine.create_edit("demo.txt", "after")
    tx = engine.apply([edit])
    assert target.read_text(encoding="utf-8") == "after"

    engine.rollback(tx.id)
    assert target.read_text(encoding="utf-8") == "before"


def test_vector_memory_search(tmp_path):
    (tmp_path / "a.py").write_text("class PluginModule:\\n    pass\\n", encoding="utf-8")
    memory = VectorMemory(tmp_path).build_from_files()
    results = memory.search("plugin module")
    assert results
    assert results[0]["path"] == "a.py"


def test_security_scanner_stronger_patterns(tmp_path):
    (tmp_path / "bad.py").write_text("import pickle\npickle.load(open('x','rb'))\n", encoding="utf-8")
    scanner = SecurityScanner(tmp_path).scan()
    assert any(f.kind == "pickle_load" for f in scanner.findings)
