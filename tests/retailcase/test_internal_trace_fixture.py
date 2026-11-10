from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "api/wms_api_server"), str(ROOT / "tests/tradecase")]

from app.modules.inventory.domain.trace_manifest import parse_manifest, resolve_aggregates, validate_units
from internal_trace_fixture import build_manifest


def test_internal_fixture_is_exact_trace_manifest_with_unique_physical_units():
    profiles = [{"system_code": "CRPT", "profile_code": "TOBACCO", "version": "TC03"}]
    document = build_manifest(tag="A1", warehouse_id=123, article="SKU", gtin="29001445629981", policy_version=1, profiles=profiles)
    parsed = parse_manifest(__import__("json").dumps(document))
    known = {("CRPT", "TOBACCO"): {"version": "TC03", "mode": "UNIT"}}
    units = validate_units(parsed, known, "29001445629981")
    aggregates = resolve_aggregates(parsed, units, known)
    assert len(units) == 250
    assert len({item["codes"][0]["code"] for item in document["units"]}) == 250
    assert aggregates[0]["level"] == "PALLET"
    assert len(aggregates[0]["units"]) == 250

def test_internal_fixture_rejects_unsafe_tags_and_empty_profiles():
    args = dict(warehouse_id=123, article="SKU", gtin="29001445629981", policy_version=1, profiles=[])
    try:
        build_manifest(tag="bad-tag", **args)
    except ValueError as error:
        assert "tag" in str(error)
    else:
        raise AssertionError("unsafe tag accepted")
    try:
        build_manifest(tag="A1", **args)
    except ValueError as error:
        assert "profile" in str(error)
    else:
        raise AssertionError("empty profile set accepted")


def test_internal_fixture_supplies_full_egais_code_when_profile_requires_it():
    profiles = [
        {"system_code": "CRPT", "profile_code": "TOBACCO", "version": "QR1"},
        {"system_code": "EGAIS", "profile_code": "ALCOHOL", "version": "QR1"},
    ]
    document = build_manifest(tag="A1", warehouse_id=123, article="SKU", gtin="29001445629981", policy_version=1, profiles=profiles, quantity=2)
    assert all(len(unit["codes"][1]["code"]) == 68 for unit in document["units"])
