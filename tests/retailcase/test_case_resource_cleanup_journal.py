"""Pure durable cleanup retry protection; no Oracle connection or mutation."""
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("case_cleanup_review", ROOT / "scripts/case_resource_commands_cleanup.py")
assert SPEC and SPEC.loader
cleanup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cleanup)


@pytest.fixture
def intent(monkeypatch):
    monkeypatch.setattr(cleanup, "save", lambda report: None)
    source = {"case_task_id": 1138}
    metadata = {"allow_empty": True, "destinations": {}, "scan_container": "fixture-carrier", "expected_content_version": 3, "reason": "owned fixture retirement"}
    report = {}
    command = cleanup.frozen(report, "EMPTY", "CASE_CARRIER_RETURN", source, metadata)
    return report, source, metadata, command


def test_lost_ack_retry_retains_original_version_and_bytes(intent):
    report, source, metadata, command = intent
    retried = cleanup.frozen(report, "EMPTY", "CASE_CARRIER_RETURN", source, {**metadata, "expected_content_version": 4})
    assert retried.canonical_json() == command.canonical_json()
    assert retried.metadata["expected_content_version"] == 3


@pytest.mark.parametrize("field,value", [
    ("operation_id", "CRES15.CLEANUP.FOREIGN"),
    ("command_type", "WAVE_CANCEL"),
    ("actor", "other-actor"),
    ("source", {"case_task_id": 1136}),
    ("allow_empty", False),
    ("destinations", {"foreign-lot": "foreign-cell"}),
    ("scan_container", "different-carrier"),
    ("reason", "different requested action"),
    ("expected_content_version", True),
    ("expected_content_version", -1),
])
def test_self_canonical_but_retargeted_or_corrupt_journal_refused(intent, field, value):
    report, source, metadata, _ = intent
    data = json.loads(report["commands"]["EMPTY"])
    if field in data["metadata"]:
        data["metadata"][field] = value
    else:
        data[field] = value
    forged = cleanup.StockCommand(data["operation_id"], data["command_type"], data["actor"], (), data["source"], metadata=data["metadata"])
    report["commands"]["EMPTY"] = forged.canonical_json()
    retained = report["commands"]["EMPTY"]
    with pytest.raises(AssertionError):
        cleanup.frozen(report, "EMPTY", "CASE_CARRIER_RETURN", source, metadata)
    assert report["commands"]["EMPTY"] == retained


def lineage_rows():
    common = dict(cell="QIPcdbf4c0962", stock_origin_uid="300000034518661218")
    return [dict(common, uid_poleta="parent", remain=23, hard_reserved_base=1, stock_version=12, created_by_stock_op="original-parent"),
            dict(common, uid_poleta="child", remain=1, hard_reserved_base=0, stock_version=4, created_by_stock_op="WHREQ15.ASM.PICK1136")]


def test_lineage_allows_only_legitimate_parent_reservation_release():
    before = lineage_rows()
    after = deepcopy(before)
    after[0].update(hard_reserved_base=0, stock_version=13)
    cleanup.verify_lineage(before, after, {"source": "parent"})


@pytest.mark.parametrize("field,value", [("remain", 0), ("cell", "wrong-cell"), ("stock_origin_uid", "wrong-origin"), ("created_by_stock_op", "wrong-operation"), ("hard_reserved_base", 1)])
def test_child_physical_or_lineage_change_refused(field, value):
    before = lineage_rows()
    after = deepcopy(before)
    after[0].update(hard_reserved_base=0, stock_version=13)
    after[1][field] = value
    with pytest.raises(AssertionError):
        cleanup.verify_lineage(before, after, {"source": "parent"})
