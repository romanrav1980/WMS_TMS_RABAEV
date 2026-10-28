"""C-0193 offline: one root HU (KG + EA CASE children) binds to one ST for one recipient; every refusal writes nothing (fake Oracle)."""
import copy
import inspect
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.wms_api_server.app.auth import AdminUser, get_current_admin
from api.wms_api_server.app.modules.inventory.api.root_shipment_routes import router
from api.wms_api_server.app.modules.inventory.contracts_root_shipment import RootShipmentBindRequest, RootShipmentError, root_shipment_service
from api.wms_api_server.app.modules.inventory.infrastructure import root_shipment_binding as binding


def world():
    return {
        "st": {"uid": "MT.ST.PAL", "id": 900, "ware": 7, "condition": 0, "supplier": None},
        "tasks": {11: [501, 7, "SS11", "WAIT_CONTROL", 3, None], 12: [502, 7, "SS12", "WAIT_CONTROL", 2, None]},
        "fulfillments": [[301, 501, "PLANNED", "STORE 1"], [302, 502, "PLANNED", "STORE 1"]],
        "carrier": {11: [("MTK", "KG", "9.6")], 12: [("MTE", "EA", "4")]},
        "st_rows": [("MTK", "9.6", "KG", 1, 1, 6), ("MTE", "4", "EA", 1, 1, 0)],
        "snapshot": {"root": "MT.PAL", "warehouse": 7, "ancestors": [], "nodes": [
            {"uid": "MT.PAL", "kind": "CONTAINER", "type": "PALLET", "version": 5},
            {"uid": "CASE:11", "kind": "CASE", "case_task_id": 11, "sscc": "SS11", "version": 3},
            {"uid": "L1", "kind": "STOCK", "case_task_id": 11, "article": "MTK", "base_uom": "KG", "quantity": "9.6"},
            {"uid": "CASE:12", "kind": "CASE", "case_task_id": 12, "sscc": "SS12", "version": 2},
            {"uid": "L2", "kind": "STOCK", "case_task_id": 12, "article": "MTE", "base_uom": "EA", "quantity": "4"}]},
        "events": [], "writes": [],
    }


class Cursor:
    def __init__(self, db):
        self.db, self.rows, self.rowcount = db, [], 0

    def setinputsizes(self, **k):
        pass

    def callfunc(self, name, kind, args):
        assert name == "RRL_STOCK_HU_READ.snapshot_json"
        snap = self.db["snapshot"]
        if args[0] != snap["root"]:
            import oracledb
            raise oracledb.DatabaseError("not found")
        return json.dumps(snap)

    def execute(self, sql, binds=None):
        db, b = self.db, binds or {}
        self.rows = []
        if sql.startswith("begin RRL_STOCK_METADATA_TX"):
            return
        if "from RRL_SBORKA_PALLETS where PALLET_UID" in sql:
            st = db["st"]
            self.rows = [(st["id"], st["ware"], st["condition"], st["supplier"])] if b["p"] == st["uid"] else []
        elif "from RRL_CASE_PICK_EVENT" in sql:
            self.rows = [(e["payload"],) for e in db["events"] if e["event"] == b["e"] and e["offline"].startswith(b["prefix"])]
        elif sql.startswith("select count(*) from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID"):
            self.rows = [(sum(1 for t in db["tasks"].values() if t[5] == b["sid"]),)]
        elif "from RRL_CASE_PICK_TASK" in sql and "for update" in sql:
            ids = set(b.values())
            self.rows = [(tid, *row) for tid, row in sorted(db["tasks"].items()) if tid in ids]
        elif "from RRL_CUSTOMER_ORDER_FULFILLMENT" in sql:
            self.rows = [tuple(f) for f in db["fulfillments"]]
        elif "from RRL_CASE_CARRIER_LOT" in sql:
            self.rows = list(db["carrier"].get(b["id"], []))
        elif "from RRL_SBORKA_PALLET_ROWS" in sql:
            self.rows = list(db["st_rows"])
        elif sql.startswith("update RRL_CASE_PICK_TASK"):
            row = db["tasks"][b["id"]]
            self.rowcount = 0
            if row[5] is None:
                row[5] = b["sid"]; self.rowcount = 1
            db["writes"].append(("task", b["id"], b["sid"]))
        elif sql.startswith("update RRL_CUSTOMER_ORDER_FULFILLMENT"):
            f = next(f for f in db["fulfillments"] if f[0] == b["fid"])
            self.rowcount = int(f[2] == "PLANNED")
            f[2] = "PICKED"
            db["writes"].append(("fulfillment", b["fid"], b["task_id"], json.loads(b["composition_json"])))
        elif sql.startswith("insert into RRL_CASE_PICK_EVENT"):
            db["events"].append({"event": b["event"], "offline": b["event_id"], "payload": b["event_json"]})
            db["writes"].append(("event", b["event_id"]))
        else:
            raise AssertionError("unexpected SQL: " + sql[:80])

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return list(self.rows)

    def fetchmany(self, n):
        return list(self.rows[:n])


class Gateway:
    def __init__(self, db):
        self.db = db

    def transaction(self, purpose):
        db = self.db

        class Scope:
            def __enter__(self): return Cursor(db)
            def __exit__(self, *e): return False
        return Scope()


def request(**change):
    return RootShipmentBindRequest(**({"operation_id": "MT.BIND.1", "shipment_identifier": "MT.ST.PAL", "scanned_root": "MT.PAL", "expected_root_version": 5} | change))


def test_two_case_kg_ea_root_binds_to_one_st_for_one_recipient():
    db = world()
    result = binding.RootShipmentBinding(Gateway(db)).bind(request(), "picker")
    assert result["status"] == "BOUND" and result["shipment_id"] == 900 and result["idempotent"] is False
    assert {t: row[5] for t, row in db["tasks"].items()} == {11: 900, 12: 900}  # every child -> the same ST, no split
    picked = {w[1]: (w[2], w[3]) for w in db["writes"] if w[0] == "fulfillment"}
    assert picked == {301: (11, [{"article": "MTK", "base_uom": "KG", "quantity": "9.6"}]), 302: (12, [{"article": "MTE", "base_uom": "EA", "quantity": "4"}])}
    assert sorted(e["offline"] for e in db["events"]) == ["MT.BIND.1:11", "MT.BIND.1:12"]


def test_exact_replay_returns_the_stored_result_without_new_effects():
    db = world()
    service = binding.RootShipmentBinding(Gateway(db))
    first = service.bind(request(), "picker")
    writes = list(db["writes"])
    again = service.bind(request(), "picker")
    assert again == dict(first, idempotent=True) and db["writes"] == writes


@pytest.mark.parametrize("change,actor", [({"expected_root_version": 4}, "picker"), ({"scanned_root": "MT.PAL.OTHER"}, "picker"), ({}, "other")])
def test_changed_body_or_actor_under_the_same_operation_conflicts(change, actor):
    db = world()
    service = binding.RootShipmentBinding(Gateway(db))
    service.bind(request(), "picker")
    writes = list(db["writes"])
    with pytest.raises(RootShipmentError) as refused:
        service.bind(request(**change), actor)
    assert refused.value.code == "OPERATION_CONTENT_CONFLICT" and db["writes"] == writes


def mutate(path, value):
    def apply(db):
        target = db
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return apply


REFUSALS = [
    (mutate(("tasks", 12, 5), 777), "ROOT_CASE_ALREADY_BOUND_TO_ANOTHER_ST"),
    (lambda db: db["tasks"].pop(12), "ROOT_CASE_MISSING_OR_FOREIGN"),
    (mutate(("tasks", 12, 1), 8), "ROOT_CASE_FOREIGN_WAREHOUSE"),
    (mutate(("tasks", 12, 3), "IN_PROGRESS"), "ROOT_CASE_NOT_CLOSED"),
    (mutate(("tasks", 12, 4), 9), "ROOT_CASE_VERSION_CHANGED"),
    (mutate(("tasks", 12, 0), 501), "ROOT_CASE_ORDER_NOT_UNIQUE"),
    (mutate(("fulfillments", 1, 3), "STORE 2"), "ST_RECIPIENT_NOT_SINGLE"),
    (lambda db: db["fulfillments"].append([303, 503, "PLANNED", "STORE 1"]), "ST_FULFILLMENT_ORDERS_DIFFER_FROM_ROOT"),
    (mutate(("fulfillments", 0, 2), "PICKED"), "ST_FULFILLMENT_NOT_SINGLE_PLANNED"),
    (mutate(("snapshot", "nodes", 0, "version"), 6), "ROOT_VERSION_CHANGED"),
    (mutate(("carrier", 12), [("MTE", "EA", "3")]), "ROOT_COMPOSITION_CHANGED"),
    (mutate(("st_rows",), [("MTK", "9.6", "KG", 1, 1, 6), ("MTE", "5", "EA", 1, 1, 0)]), "ST_COMPOSITION_DIFFERS_FROM_ROOT"),
    (lambda db: db["tasks"].__setitem__(99, [599, 7, "SS99", "WAIT_CONTROL", 1, 900]), "ST_ALREADY_BOUND_TO_ANOTHER_PHYSICAL_ROOT"),
    (mutate(("snapshot", "nodes", 0, "type"), "ROLL_CAGE"), "ROOT_PALLET_OR_BOX_REQUIRED"),
    (mutate(("snapshot", "ancestors"), [{"uid": "OUTER"}]), "ROOT_MUST_BE_TOP_LEVEL"),
    (mutate(("st", "ware"), 8), "ST_WAREHOUSE_OR_STATE_MISMATCH"),
]


@pytest.mark.parametrize("apply,code", REFUSALS)
def test_every_refusal_writes_nothing(apply, code):
    db = world()
    apply(db)
    with pytest.raises(RootShipmentError) as refused:
        binding.RootShipmentBinding(Gateway(db)).bind(request(), "picker")
    assert refused.value.code == code and db["writes"] == [] and db["events"] == []


def test_unknown_root_or_st_is_404():
    with pytest.raises(RootShipmentError) as refused:
        binding.RootShipmentBinding(Gateway(world())).bind(request(scanned_root="NOPE"), "picker")
    assert (refused.value.code, refused.value.status) == ("ROOT_NOT_FOUND", 404)
    with pytest.raises(RootShipmentError) as refused:
        binding.RootShipmentBinding(Gateway(world())).bind(request(shipment_identifier="NOPE"), "picker")
    assert (refused.value.code, refused.value.status) == ("ST_NOT_FOUND", 404)


def test_source_binds_all_children_to_one_st_and_never_changes_the_tree_or_stock():
    source = inspect.getsource(binding)
    assert source.count("LEGACY_SBORKA_PALLET_ID=:sid,") == 1  # one ST id for every child in _write
    for forbidden in ("/detach", "HU_DETACH", "detach_case(", "RRL_WMS_HU_LINK", "update RRL_REMAINS", "StockPosting", "RRL_SBORKA_PALLETS_ADD", "insert into RRL_SBORKA"):
        assert forbidden not in source, forbidden
    assert "for update" in source and "receipt_task_metadata" in source  # locks + the supported metadata boundary


def test_operation_id_fits_the_event_key():
    with pytest.raises(Exception):
        request(operation_id="X" * 81)


class Service:
    def __init__(self, error=None):
        self.error, self.calls = error, []

    def bind(self, body, actor):
        self.calls.append(actor)
        if self.error:
            raise self.error
        return {"status": "BOUND"}


def client(service, permissions):
    app = FastAPI(); app.include_router(router)
    app.dependency_overrides[get_current_admin] = lambda: AdminUser("picker", "Picker", "QA", set(permissions))
    app.dependency_overrides[root_shipment_service] = lambda: service
    return TestClient(app, raise_server_exceptions=False)


BODY = {"operation_id": "MT.BIND.1", "shipment_identifier": "MT.ST.PAL", "scanned_root": "MT.PAL", "expected_root_version": 5}


def test_route_requires_case_pick_execute_and_maps_refusals():
    service = Service()
    assert client(service, {"case_pick_view"}).post("/api/warehouse-hus/bind-shipment", json=BODY).status_code == 403 and service.calls == []
    assert client(service, {"case_pick_execute"}).post("/api/warehouse-hus/bind-shipment", json=BODY).json() == {"status": "BOUND"}
    refused = client(Service(RootShipmentError("ST_RECIPIENT_NOT_SINGLE")), {"case_pick_execute"}).post("/api/warehouse-hus/bind-shipment", json=BODY)
    assert refused.status_code == 409 and refused.json()["detail"]["code"] == "ST_RECIPIENT_NOT_SINGLE" and refused.json()["detail"]["outcome_confirmed"] is True
    conflict = client(Service(RootShipmentError("OPERATION_CONTENT_CONFLICT")), {"case_pick_execute"}).post("/api/warehouse-hus/bind-shipment", json=BODY)
    assert conflict.json()["detail"]["operation_id_conflict"] is True and conflict.json()["detail"]["outcome_confirmed"] is False
    assert client(service, {"case_pick_execute"}).post("/api/warehouse-hus/bind-shipment", json=BODY | {"fact_qty": "1"}).status_code == 422


def test_main_registers_the_route_with_a_constructible_service():
    from api.wms_api_server.app.main import app
    assert "/api/warehouse-hus/bind-shipment" in {getattr(r, "path", "") for r in app.routes}
    service = app.dependency_overrides[root_shipment_service]()  # resolves names in main (no NameError) without touching Oracle
    assert isinstance(service, binding.RootShipmentBinding)
