"""Root HU tare booking keeps the root scan/version inside the native command."""
from pathlib import Path

import pytest

from api.wms_api_server.app.modules.inventory.api import tare_assembly_routes as routes


def test_hu_root_scans_are_forwarded_to_native_metadata(monkeypatch):
    captured = {}

    def fake_command(service, kind, operation_id, source, metadata, user):
        captured.update(kind=kind, operation_id=operation_id, source=source, metadata=metadata)
        return {"status": "HELD"}

    monkeypatch.setattr(routes, "command", fake_command)
    body = routes.Book(operation_id="ROOT.TARE.1", place_kind="HU", place_id="ROOT-1",
                       expected_warehouse_id=7, pallet_type_id=2, expected_root_version=4,
                       scan_place="ROOT-1", scan_cell="PACK-1")
    result = routes.book(body, user=type("User", (), {"username": "picker"})(), service=object())

    assert result == {"status": "HELD"}
    assert captured == {
        "kind": "TARE_BOOK", "operation_id": "ROOT.TARE.1",
        "source": {"place_kind": "HU", "place_id": "ROOT-1"},
        "metadata": {"pallet_type_id": 2, "expected_warehouse_id": 7,
                     "expected_root_version": 4, "scan_place": "ROOT-1", "scan_cell": "PACK-1"},
    }


def test_root_scan_fields_are_rejected_for_case():
    with pytest.raises(ValueError, match="Root scan fields"):
        routes.Book(operation_id="CASE.TARE.1", place_kind="CASE", place_id="12",
                    expected_root_version=1)


def test_oracle_migration_checks_root_version_and_both_scans():
    sql = Path("db/migrations/2026-10-28_root_hu_tare_scans/001_root_hu_tare_book_scans.sql").read_text(encoding="utf-8")
    for refusal in ("TARE_ROOT_VERSION_CHANGED", "TARE_ROOT_SCAN_REQUIRED", "TARE_ROOT_CELL_SCAN_REQUIRED"):
        assert refusal in sql
    assert "v_goods_kind='CONTAINER'" in sql
    assert "p_domain.put('expected_root_version'" in sql
