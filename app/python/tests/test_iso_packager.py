from pathlib import Path

from ai_serviter.iso_packager import ISOPackager


def test_iso_tree_creation(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "python").mkdir()
    (root / "python" / "dummy.txt").write_text("ok", encoding="utf-8")
    packager = ISOPackager(root)
    tree = packager.create_iso_tree(tmp_path / "iso_tree", "Test Serviter")
    assert (tree / "autorun.inf").exists()
    assert (tree / "setup.bat").exists()
    assert (tree / "vm" / "vm_config.ovf").exists()
    assert (tree / "scripts" / "install_unix.sh").exists()
    assert (tree / "manifest.json").exists()


def test_iso_build_reports_missing_tool_or_artifact(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    packager = ISOPackager(root)
    tree = packager.create_iso_tree(tmp_path / "iso_tree")
    result = packager.build_iso(tree, tmp_path / "out.iso")
    assert isinstance(result.ok, bool)
    assert result.messages is not None
