from pathlib import Path
from ai_serviter.update_security import UpdateSecurity

def test_update_security_sha_and_hmac(tmp_path):
    f = tmp_path / "artifact.zip"
    f.write_bytes(b"hello")
    sec = UpdateSecurity()
    digest = sec.sha256(f)
    assert sec.verify_sha256(f, digest)["ok"]
    sig = sec.hmac_sign(f, "secret")
    assert sec.hmac_verify(f, "secret", sig)["ok"]

def test_installer_files_exist():
    root = Path(__file__).resolve().parents[2]
    assert (root / "installer/build/build_linux_package.sh").exists()
    assert (root / "installer/build/build_windows_installer.ps1").exists()
    assert (root / "installer/signing/sign_windows.ps1").exists()
    assert (root / "installer/update/release-manifest.example.json").exists()
