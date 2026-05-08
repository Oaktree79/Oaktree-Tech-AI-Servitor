from pathlib import Path

from ai_serviter.certificate_manager import CertificateInventory
from ai_serviter.certificate_store import CertificateStore
from ai_serviter.database import ServiterDatabase


def test_certificate_inventory_loads_schema_tolerant_csv(tmp_path):
    csv_path = tmp_path / "certs.csv"
    csv_path.write_text(
        "Common Name,Issuer,Serial Number,Expiration Date\n"
        "example.com,Example CA,123,2099-01-01\n"
        "expired.example.com,Example CA,456,2000-01-01\n",
        encoding="utf-8",
    )
    inv = CertificateInventory().load_csv(csv_path)
    assert inv.summary()["total_certificates"] == 2
    findings = inv.findings()
    assert any(f.kind == "expired" for f in findings)


def test_certificate_store_imports_csv(tmp_path):
    csv_path = tmp_path / "certs.csv"
    csv_path.write_text("cn,issuer,expires\nexample.com,CA,2099-01-01\n", encoding="utf-8")
    db = ServiterDatabase(tmp_path / "serviter.db")
    store = CertificateStore(db)
    result = store.import_csv(csv_path)
    assert result["summary"]["total_certificates"] == 1
    assert store.latest()["summary"]["total_certificates"] == 1
