"""C-0176 offline checks: the NOT_APPLIED selected-places kit, the strict command contract and the outcome flags of the API."""
import hashlib
import json
import pathlib
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.modules.transport.api.place_removal_routes import router
from app.modules.transport.contracts_place_removal import PlaceRemovalCommand, PlaceRemovalError, place_removal_service

KIT = pathlib.Path(__file__).resolve().parents[2] / "db/migrations/2026-10-27_tt_selected_places"
HASH = "A" * 64


def text(name):
    return (KIT / name).read_text(encoding="utf-8")


def test_kit_hashes_writer_edit_and_guarded_rollback():
    m = json.loads(text("manifest.json"))
    assert m["status"] == "NOT_APPLIED" and not m["applied_by_claude"]
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    writer = text("002_writer.sql")
    assert "p_member_id number default null" in writer and "TRIP_MEMBER_SELECTION_REMOVAL_ONLY" in writer
    assert writer.count("and(p_member_id is null or ID=p_member_id)") == 2  # discovery and the snapshot count use the same selection
    body = text("004_removal_body.sql")
    remove = body[body.index(" procedure remove("):]
    assert remove.index("lock table RRL_ACCESS_REV in share mode") < remove.index("RRL_ACCESS_API.allowed") < remove.index("TRADE_OWNER_ACCESS_DENIED") < remove.index("if replay(")
    # The stored reply is read again after the trip lock, before the snapshot check: a concurrent exact repeat gets the same receipt.
    after_lock = remove[remove.index("for update"):]
    assert after_lock.index("if replay(") < after_lock.index("TRIP_MEMBERSHIP_SNAPSHOT_CHANGED") < after_lock.index("RRL_TT_ADD_PALL(0,v_st,v_id)")
    assert "exception when dup_val_on_index then fail('OPERATION_CONFLICT')" in body and "ST_WAREHOUSE_REQUIRED" in body and "rownum<=1001" in body
    assert "p_result:=old.RESULT_JSON;return true;" in body and "replayed" not in body
    rollback = text("rollback.sql")
    assert rollback.index("AFTER_SOURCE_DRIFT_REFUSED") < rollback.index("TT_PLACE_REMOVAL_HISTORY_PRESENT") < rollback.index("@@before_writer.sql") \
        < rollback.index("drop table RRL_TT_PLACE_REMOVAL_CMD")


def test_command_contract_is_strict():
    ok = dict(operation_id="TT.PLACES.1", st_number="ST1", member_ids=[5, 6], expected_source_hash=HASH, reason="Reduced trip")
    assert PlaceRemovalCommand(**ok).member_ids == [5, 6]
    for bad in (dict(member_ids=["5"]), dict(member_ids=[True]), dict(member_ids=[5, 5]), dict(member_ids=[0]), dict(member_ids=[]),
                dict(expected_source_hash="a" * 64), dict(member_ids=list(range(1, 202)))):
        with pytest.raises(ValidationError):
            PlaceRemovalCommand(**dict(ok, **bad))


class Refusing:
    def __init__(self, code, status):
        self.code, self.status = code, status

    def places(self, trip, st, actor):
        raise PlaceRemovalError(self.code, self.status)

    def remove(self, trip, body, actor):
        raise PlaceRemovalError(self.code, self.status)


@pytest.mark.parametrize("code,status,confirmed,retry", [
    ("TRIP_MEMBERSHIP_SNAPSHOT_CHANGED", 409, True, False),
    ("OPERATION_CONFLICT", 409, False, False),
    ("ACCESS_DENIED", 403, False, False),
    ("PLACE_REMOVAL_RESULT_UNKNOWN", 503, False, True),
])
def test_command_outcome_flags(monkeypatch, code, status, confirmed, retry):
    app = FastAPI(); app.include_router(router)
    from app.modules.transport.api import place_removal_routes
    app.dependency_overrides[place_removal_service] = lambda: Refusing(code, status)
    app.dependency_overrides[place_removal_routes.get_current_user] = lambda: type("U", (), {"username": "qa"})()
    r = TestClient(app).post("/api/transport/trips/1/place-removals", json=dict(operation_id="TT.PLACES.1", st_number="ST1", member_ids=[5],
                                                                               expected_source_hash=HASH, reason="Reduced trip"))
    assert r.status_code == status and r.json()["detail"] == {"code": code, "outcome_confirmed": confirmed, "retry_same_operation_id": retry}
