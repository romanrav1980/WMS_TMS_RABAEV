"""C-0191 T06/T07: control, loading, departure and store receipt of the C0190 mixed pallet (KG + EA CASE children, one recipient).

Takes the C0190 Live object after its TREE stage (warehouse, cases, parent "<tag>.PAL", journal, send/post/read/one/composition)
and drives the existing native flow used by tests/tradecase/live_nested_shipping.py and scripts/case380_marked_small_receipt.py:
one legacy shipment (ST) for the single recipient with both CASE children bound to it, a transport task with the ST, vehicle
profile, physical floor type of the root, outgoing quality, root tare, nested LOAD, tare handover to a separate driver, DEPART
and the store receipt of the one root pallet by its identifier. Children are never split across recipients.

Every write goes through the C0190 journal (stored before sending, replayed byte-for-byte, an unknown outcome blocks the rest).
Values that come from the software fixture are marked SYNTHETIC in their evidence/measurement references; nothing here is a
physical measurement or a production external acknowledgement. A departure that needs a real transport document stops with
EXTERNAL_TRANSPORT_DOCUMENT_REQUIRED; a store place that needs marked-unit scans stops with STORE_MARKED_RECIPIENT_FLOW_REQUIRED.
Importing this module performs no live work; root executes it through C0190 (or `run(live, inputs)`).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import secrets
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("c0190_runner", ROOT / "scripts/c0190_mixed_tree_runner.py")
c0190 = sys.modules.get("c0190_runner") or importlib.util.module_from_spec(_SPEC)
if "c0190_runner" not in sys.modules:
    sys.modules["c0190_runner"] = c0190
    _SPEC.loader.exec_module(c0190)  # pure helpers only; C0190 does no live work at import
RunnerStop, tree_findings, attach_case_body = c0190.RunnerStop, c0190.tree_findings, c0190.attach_case_body

STAGES = ("SHIPMENT", "TRANSPORT_TASK", "FLOOR_QC_TARE", "LOAD", "TARE_HANDOVER", "DEPART", "STORE_RECEIPT")
ORIGINS = {"SYNTHETIC_FIXTURE", "OPERATOR_MEASURED"}
_NUM = r"[0-9]{1,18}(\.[0-9]{1,9})?"


# ---------------------------------------------------------------- input contract (validated, offline-tested)

def validate_inputs(inputs: dict[str, Any]) -> list[str]:
    """The fixture inputs the native flow needs and the current C0190 state does not hold. Empty list = complete."""
    out = []
    text = lambda k, n=50: isinstance(inputs.get(k), str) and 0 < len(inputs[k].strip()) <= n
    for key, limit in (("store_address", 255), ("vehicle_number", 50), ("dock", 50), ("driver_name", 100), ("paper_reference", 200)):
        if not text(key, limit):
            out.append(f"INPUT_REQUIRED:{key}")
    if not isinstance(inputs.get("pallet_type_id"), int) or inputs["pallet_type_id"] < 1:
        out.append("INPUT_REQUIRED:pallet_type_id")
    if not (isinstance(inputs.get("shipment_date"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", inputs["shipment_date"])):
        out.append("INPUT_REQUIRED:shipment_date")
    if not isinstance(inputs.get("store_policy_expected_version"), int) or inputs["store_policy_expected_version"] < 0:
        out.append("INPUT_REQUIRED:store_policy_expected_version")
    m = inputs.get("root_measurements") or {}
    if m.get("origin") not in ORIGINS:
        out.append("INPUT_REQUIRED:root_measurements.origin")
    for key in ("gross_weight_kg", "width_m", "depth_m", "height_m"):
        if not (isinstance(m.get(key), str) and re.fullmatch(_NUM, m[key]) and Decimal(m[key]) > 0):
            out.append(f"INPUT_REQUIRED:root_measurements.{key}")
    qc = inputs.get("qc") or {}
    if qc.get("mode") not in ("SCAN", "WEIGHT"):
        out.append("INPUT_REQUIRED:qc.mode")
    if qc.get("mode") == "WEIGHT":
        if qc.get("origin") not in ORIGINS:
            out.append("INPUT_REQUIRED:qc.origin")
        for key in ("gross_weight", "wood_weight"):
            if not (isinstance(qc.get(key), str) and re.fullmatch(_NUM, qc[key])):
                out.append(f"INPUT_REQUIRED:qc.{key}")
    g = inputs.get("vehicle_geometry") or {}
    for key in ("cargo_length_mm", "cargo_width_mm", "cargo_height_mm", "outer_height_mm", "outer_length_mm", "max_places"):
        if not isinstance(g.get(key), int) or g[key] < 1:
            out.append(f"INPUT_REQUIRED:vehicle_geometry.{key}")
    return out


DOCID_MAX = 15  # RRL_SBORKA_PALLET_ROWS.DOCID VARCHAR2(15); ST_NUMBER itself allows 50


def st_number_for(tag: str) -> str:
    """K-0224: the ST number goes into DOCID (<=15). Deterministic from the unique run tag (same value on resume, any tag format);
    a collision is refused by the read-only check before the first write."""
    if not isinstance(tag, str) or not tag:
        raise RunnerStop("RUN_TAG_MISSING")
    st = "ST" + hashlib.sha256(tag.encode("utf-8")).hexdigest()[:DOCID_MAX - 2].upper()
    assert len(st) == DOCID_MAX
    return st


FULFILLMENT_SQL = ("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,"
                   "FACT_WEIGHT,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,:o,:s,:u,:a,'PLANNED',0,0,'QA_C0191_ONLY',systimestamp,'admin')")


def shipment_intent(key: str, kind: str, target: str, args: Any) -> dict[str, Any]:
    """Deterministic, JSON-safe descriptor of one SHIPMENT metadata command (Decimal/date as text, binds sorted)."""
    if kind not in ("CALL", "EXEC"):
        raise RunnerStop(f"SHIPMENT_INTENT_KIND:{kind}")
    safe = json.loads(json.dumps(args if kind == "CALL" else dict(sorted(dict(args).items())), default=str, sort_keys=True))
    return {"operation": key, "kind": kind, "target": target, "args": safe}


def fulfillment_match(rows: list[tuple], uid: str, address: str) -> int | None:
    """K-0231: exactly one row with this run's shipment UID, address, PLANNED, zero fact quantity/weight and QA_C0191_ONLY; any other
    row under the same order/ST stops before a duplicate insert."""
    if not rows:
        return None
    if len(rows) > 1:
        raise RunnerStop(f"FULFILLMENT_DUPLICATE:{len(rows)}")
    fid, pallet_uid, addr, status, qty, weight, source = rows[0]
    if (pallet_uid, addr, status, source) != (uid, address, "PLANNED", "QA_C0191_ONLY") or Decimal(str(qty or 0)) != 0 or Decimal(str(weight or 0)) != 0:
        raise RunnerStop(f"FULFILLMENT_MISMATCH:{rows[0]}")
    return int(fid)


def evidence(origin: str, tag: str, what: str) -> str:
    """Reference text that never presents fixture values as physical measurements (<=100 chars)."""
    prefix = "SYNTHETIC_FIXTURE_NOT_PHYSICAL" if origin == "SYNTHETIC_FIXTURE" else "OPERATOR_MEASURED"
    return f"{prefix}:{what}:{tag}"[:100]


def loading_body(tag: str, root: str, composition: dict[str, Any], task: int, inputs: dict[str, Any]) -> dict[str, Any]:
    """Nested LOAD of the single root pallet; CASE children travel inside it (no BOX containers, so no physical_boxes)."""
    node, m = composition["nodes"][0], inputs["root_measurements"]
    return {"operation_id": f"{tag}.LOAD", "identifier": root, "expected_version": node["version"], "scan_container": root,
            "scan_cell": node["cell"], "transport_task_id": task, "scan_vehicle": inputs["vehicle_number"], "scan_dock": inputs["dock"],
            "measurements": {"origin": "MANUAL_CONFIRMED", "content_version": node["version"], "gross_weight_kg": m["gross_weight_kg"],
                             "width_m": m["width_m"], "depth_m": m["depth_m"], "height_m": m["height_m"]}, "physical_boxes": []}


def receipt_observations(composition: dict[str, Any]) -> list[dict[str, str]]:
    """PAPER_COUNT counts per loaded STOCK leaf, exactly what the tree carried (accepted = loaded quantity)."""
    leaves = [n for n in composition.get("nodes", []) if n.get("kind") == "STOCK"]
    if not leaves or len({n["uid"] for n in leaves}) != len(leaves):
        raise RunnerStop("STORE_OBSERVATIONS_NEED_UNIQUE_STOCK_LEAVES")
    return [{"lot_uid": n["uid"], "accepted": str(n["quantity"])} for n in leaves]


def store_receipt_body(tag: str, load_op: str, preview: dict[str, Any], inputs: dict[str, Any], observations: list[dict[str, str]], root: str) -> dict[str, Any]:
    if preview.get("already_received"):
        raise RunnerStop("STORE_PLACE_ALREADY_RECEIVED")
    if preview.get("requires_marked_recipient_flow"):
        raise RunnerStop("STORE_MARKED_RECIPIENT_FLOW_REQUIRED: unit scans are needed; not invented here")
    if preview.get("mode") != "PAPER_COUNT":
        raise RunnerStop(f"STORE_POLICY_NOT_PAPER_COUNT:{preview.get('mode')}")
    if preview.get("root_scan_identifier") != root or preview.get("store_address") != inputs["store_address"]:
        raise RunnerStop("STORE_ROOT_OR_RECIPIENT_MISMATCH")  # one root pallet, one recipient; never split children
    return {"operation_id": f"{tag}.STORE.RECEIPT", "load_operation_id": load_op, "store_address": inputs["store_address"],
            "scan_place": root, "expected_composition_signature": preview["composition_signature"], "before_cameras": True,
            "observations": observations, "paper_reference": evidence("SYNTHETIC_FIXTURE", tag, "PAPER:" + inputs["paper_reference"])}


# ---------------------------------------------------------------- live flow (root executes through C0190)

class MixedTreeTransport:
    def __init__(self, live: Any, inputs: dict[str, Any]):
        findings = validate_inputs(inputs)
        if findings:
            raise RunnerStop("TRANSPORT_INPUTS_INCOMPLETE:" + ",".join(findings))
        if "TREE" not in live.s.get("stages_done", []):
            raise RunnerStop("C0190_TREE_NOT_VERIFIED")
        self.live, self.inputs = live, inputs
        self.t = live.s.setdefault("transport", {"inputs": inputs, "stages_done": []})
        if self.t["inputs"] != inputs:
            raise RunnerStop("TRANSPORT_INPUTS_CHANGED_AFTER_START")  # a resumed run keeps the original fixture values
        self.tag, self.ware, self.root = live.s["tag"], live.s["warehouse"], live.s["tag"] + ".PAL"

    def stage(self, name: str, fn) -> None:
        if name in self.t["stages_done"]:
            return
        self.t["stage"] = name; self.live.save()
        fn()
        self.t["stages_done"].append(name); self.t["last_verified_stage"] = name; self.live.save()

    def _metadata(self, action) -> Any:
        """Legacy shipment metadata inside the native metadata boundary (full_pallet_fixture pattern)."""
        with self.live.connect() as c:
            q = c.cursor(); q.callproc("RRL_STOCK_METADATA_TX.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                result = action(q); c.commit(); return result
            except BaseException:
                c.rollback(); raise
            finally:
                q.callproc("RRL_STOCK_METADATA_TX.end_change")

    def metadata_call(self, function: str, args: list[Any]) -> int:
        return self._metadata(lambda q: q.callfunc(function, int, args))

    def metadata_exec(self, sql: str, **binds: Any) -> None:
        self._metadata(lambda q: q.execute(sql, binds))

    def metadata_step(self, key: str, check, kind: str, target: str, args: Any) -> Any:
        """K-0224/K-0231: before every SHIPMENT metadata write the exact command descriptor (operation, CALL|EXEC, function or SQL,
        JSON-safe arguments) is persisted; a resumed run must regenerate the identical descriptor or stop. Read-only reconciliation
        before and after the write reuses only a fully matching record, so a post-commit failure never duplicates anything."""
        writes = self.t.setdefault("shipment_writes", {})
        intent = shipment_intent(key, kind, target, args)
        stored = (writes.get(key) or {}).get("intent")
        if stored is not None and stored != intent:
            raise RunnerStop(f"SHIPMENT_INTENT_CHANGED:{key}")
        found = check()
        if found is not None:
            writes[key] = {"intent": intent, "state": "DONE", "reconciled": found}; self.live.save()
            return found
        writes[key] = {"intent": intent, "state": "SENT"}; self.live.save()  # persisted before the write; unknown until the next check
        if kind == "CALL":
            self.metadata_call(target, list(args))
        else:
            self.metadata_exec(target, **dict(args))
        found = check()
        if found is None:
            raise RunnerStop(f"METADATA_WRITE_NOT_VISIBLE:{key}")
        writes[key] = {"intent": intent, "state": "DONE", "result": found}; self.live.save()
        return found

    def ensure_shipment_metadata(self, st: str, uid: str) -> None:
        live, a, address = self.live, self.live.s["articles"], self.inputs["store_address"]
        old = live.read("select ID,ST_NUMBER,WARE_ID from RRL_SBORKA_PALLETS where PALLET_UID=:u", u=uid)
        if old and len(str(old[0][1])) > DOCID_MAX:
            raise RunnerStop(f"EXISTING_ST_NUMBER_EXCEEDS_DOCID_{DOCID_MAX}:{old[0][1]}: root repairs the failed pre-rework ST before resuming")
        foreign = live.one("select (select count(*) from RRL_SBORKA_PALLETS where ST_NUMBER=:st and PALLET_UID<>:u)"
                           "+(select count(*) from RRL_SBORKA_PALLET_ROWS where DOCID=:st and PALLET_UID<>:u) from dual", st=st, u=uid)
        if foreign:
            raise RunnerStop(f"ST_NUMBER_COLLISION:{st}")

        def pallet():
            rows = live.read("select ID,ST_NUMBER,WARE_ID from RRL_SBORKA_PALLETS where PALLET_UID=:u", u=uid)
            if not rows:
                return None
            if len(rows) != 1 or rows[0][1] != st or int(rows[0][2]) != self.ware:
                raise RunnerStop(f"ST_PALLET_MISMATCH:{rows}")
            return int(rows[0][0])
        day = self.t.setdefault("st_day", str(live.one("select to_char(trunc(sysdate)+1,'YYYY-MM-DD') from dual")))  # fixed once: stable intent
        self.live.save()
        from datetime import date
        sid = self.metadata_step("st.pallet", pallet, "CALL", "RRL_SBORKA_PALLETS_ADD2", [st, address, 1, uid, "1", date.fromisoformat(day), "", "admin", self.ware])
        self.t["st_id"] = sid; live.save()
        self.metadata_step("st.condition", lambda: True if live.one("select count(*) from RRL_SBORKA_PALLETS where ID=:s and CONDITION=0", s=sid) == 1 else None,
                           "EXEC", "update RRL_SBORKA_PALLETS set CONDITION=0 where ID=:s", {"s": sid})
        for role, unit in (("kg", "KG"), ("ea", "EA")):
            qty = Decimal(live.s["measurements"]["manual_net_kg"] if role == "kg" else c0190.EA_QTY)

            def row(article=a[role], qty=qty):
                rows = live.read("select ID,QUANTITY,DOCID from RRL_SBORKA_PALLET_ROWS where PALLET_UID=:u and ARTICUL=:a", u=uid, a=article)
                if not rows:
                    return None
                if len(rows) != 1 or Decimal(str(rows[0][1])) != qty or rows[0][2] != st:
                    raise RunnerStop(f"ST_ROW_MISMATCH:{article}:{rows}")
                return int(rows[0][0])
            self.metadata_step(f"st.row.{role}", row, "CALL", "RRL_SBORKA_PALLET_ROWS_ADD4",
                               [uid, a[role], "C0191 mixed tree " + role, "", unit, 0, "", qty, "", qty, 0, None, st, self.ware, 1])
        for role in ("kg", "ea"):
            order = live.one("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where ORDER_NO=:n", n=f"{self.tag}.ORD.{role}")

            def fulfillment(order=order):
                rows = live.read("select FULFILLMENT_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,FACT_WEIGHT,SOURCE_SYSTEM from RRL_CUSTOMER_ORDER_FULFILLMENT "
                                 "where CUSTOMER_ORDER_ID=:o and LEGACY_SBORKA_PALLET_ID=:s", o=order, s=sid)
                return fulfillment_match(rows, uid, address)
            self.metadata_step(f"st.fulfillment.{role}", fulfillment, "EXEC", FULFILLMENT_SQL, {"o": order, "s": sid, "u": uid, "a": address})

    # -- SHIPMENT: one ST for the single recipient, both CASE children bound to it (detach/bind/re-attach) --
    def shipment(self) -> None:
        live, a, cases = self.live, self.live.s["articles"], self.live.s["cases"]
        uid = f"{self.tag}.ST.PAL"  # the external shipment identifier stays as before
        st = self.t.get("st_number") if len(str(self.t.get("st_number") or "")) <= DOCID_MAX and self.t.get("st_number") else st_number_for(self.tag)
        self.t.update(st_number=st, st_pallet=uid); live.save()
        self.ensure_shipment_metadata(st, uid)
        booking = {role: f"{self.tag}.TARE.BOOK.{role}" for role in cases}
        for role, case in cases.items():  # a bound CASE is required for loading; binding happens on a free carrier, then the tree is rebuilt
            version = lambda uid_: live.composition(uid_)["nodes"][0]["version"]
            child = "CASE:" + str(case["task"])
            if live.composition(child).get("ancestors"):
                live.send(f"t.detach.{role}", "POST", "/api/warehouse-hus/detach-case", {**attach_case_body(f"{self.tag}.T.DETACH.{role}", self.root, case["task"],
                          version(self.root), version(child), case["carrier"], None), "reason": "C0191 bind the CASE to its single shipment"})
            live.send(f"t.bind.{role}", "POST", f"/api/case-pick/tasks/{case['task']}/bind-shipment",
                      {"pallet_identifier": uid, "scan_container": case["carrier"], "expected_content_version": version(child)})
            live.send(f"t.reattach.{role}", "POST", "/api/warehouse-hus/attach-case",
                      attach_case_body(f"{self.tag}.T.ATTACH.{role}", self.root, case["task"], version(self.root), version(child), case["carrier"], booking[role]))
        snapshot = live.composition(self.root)
        cell = snapshot["nodes"][0]["cell"]
        findings = tree_findings(snapshot, {"case_tasks": [c["task"] for c in cases.values()], "cell": cell,
                                            "quantities": {a["kg"]: live.s["measurements"]["manual_net_kg"], a["ea"]: c0190.EA_QTY},
                                            "carriers": {c["task"]: c["carrier"] for c in cases.values()}})
        if findings:
            raise RunnerStop("TREE_AFTER_BINDING:" + ",".join(findings))
        self.t["tree_before_load"] = snapshot; live.save()

    # -- TRANSPORT_TASK: synthetic dock/vehicle/driver, one trip with the single ST, synthetic vehicle profile --
    def transport_task(self) -> None:
        live, i, base = self.live, self.inputs, "/api/admin/transport"
        if not live.read("select DOCK from RRL_TT_DOCK where DOCK=:d", d=i["dock"]):
            live.meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,ORD,COUNT_OF_PALLETS,DOCK_IS_BLOCKED)values(:d,:w,1,10,0)", d=i["dock"], w=self.ware)
        vehicle = live.send("t.vehicle", "POST", base + "/vehicles", {"num_plat": i["vehicle_number"], "transtype_id": "10", "max_weight_kg": 1000,
                            "max_pallets": i["vehicle_geometry"]["max_places"], "sobstvennyy": True}, expect=(200, 201))
        driver = live.send("t.driver", "POST", base + "/drivers", {"name": i["driver_name"], "license_number": evidence("SYNTHETIC_FIXTURE", self.tag, "LICENSE")[:50]}, expect=(200, 201))
        task = live.send("t.task", "POST", base + "/tasks", {"transtype": "10", "shipment_date": i["shipment_date"]})
        self.t.update(vehicle_id=vehicle["id"], driver_id=driver["id"], transport_task_id=task["task_id"]); live.save()
        live.send("t.task.configure", "PATCH", f"{base}/tasks/{task['task_id']}", {"transport": i["vehicle_number"], "voditel_id": driver["id"], "dock": i["dock"],
                  "shipment_time": "10:00", "primechanie": evidence("SYNTHETIC_FIXTURE", self.tag, "TRIP")})
        live.send("t.task.st", "POST", f"{base}/tasks/{task['task_id']}/sts", {"st_numbers": [self.t["st_number"]]})
        profile = live.get(f"{base}/vehicles/{vehicle['id']}/profile")
        g = i["vehicle_geometry"]
        live.send("t.profile", "POST", base + "/vehicle-profiles", {"operation_id": f"{self.tag}.PROFILE", "vehicle_id": vehicle["id"], "expected_source_hash": profile["base_hash"],
                  "expected_version": profile["version"], "vehicle_size_class": "QA_C0191", "cargo_length_mm": g["cargo_length_mm"], "cargo_width_mm": g["cargo_width_mm"],
                  "cargo_height_mm": g["cargo_height_mm"], "outer_height_mm": g["outer_height_mm"], "outer_length_mm": g["outer_length_mm"],
                  "floor_variants": [{"code": "QA_C0191", "limits": [{"pallet_type_id": i["pallet_type_id"], "max_places": g["max_places"]}]}],
                  "reason": "C0191 synthetic vehicle geometry", "evidence_reference": evidence("SYNTHETIC_FIXTURE", self.tag, "VEHICLE")})

    # -- FLOOR_QC_TARE: root physical floor type, outgoing quality of the ST, one held tare for the root --
    def floor_qc_tare(self) -> None:
        live, i = self.live, self.inputs
        floor = live.get("/api/inventory/pallet-floor-types?identifier=" + self.root)
        live.send("t.floor", "POST", "/api/inventory/pallet-floor-types", {"operation_id": f"{self.tag}.FLOOR", "identifier": self.root, "pallet_type_id": i["pallet_type_id"],
                  "expected_version": floor["version"], "scan_pallet": self.root, "scan_cell": floor["cell"],
                  "evidence_reference": evidence(i["root_measurements"]["origin"], self.tag, "FLOOR")})
        st = self.t["st_pallet"]
        current = live.get("/api/outgoing-quality/" + st)
        qc = i["qc"]
        if qc["mode"] == "SCAN":
            live.send("t.qc", "POST", f"/api/outgoing-quality/{st}/scan", {"operation_id": f"{self.tag}.QC", "expected_composition_signature": current["composition_signature"],
                      "error_count": 0, "scans": [], "item_scans": []})
        else:
            live.send("t.qc", "POST", f"/api/outgoing-quality/{st}/weight", {"operation_id": f"{self.tag}.QC", "expected_composition_signature": current["composition_signature"],
                      "gross_weight": qc["gross_weight"], "wood_weight": qc["wood_weight"], "note": evidence(qc["origin"], self.tag, "QC_WEIGHT")})
        balance = next((r for r in live.get(f"/api/inventory/tare/warehouses/{self.ware}/availability") if r["pallet_type_id"] == i["pallet_type_id"]), {})
        live.send("t.tare.count", "POST", "/api/inventory/tare/count", {"operation_id": f"{self.tag}.T.TARE.COUNT", "owner_ware_id": self.ware, "pallet_type_id": i["pallet_type_id"],
                  "condition": "GOOD", "observed_quantity": str(int(Decimal(str(balance.get("available_quantity") or 0))) + 1), "expected_version": balance.get("balance_version") or 0,
                  "reason": "C0191 synthetic root pallet count", "decision_reference": evidence("SYNTHETIC_FIXTURE", self.tag, "TARE")})
        live.send("t.tare.book", "POST", "/api/inventory/tare/book", {"operation_id": f"{self.tag}.T.TARE.BOOK", "place_kind": "HU", "place_id": self.root,
                  "expected_warehouse_id": self.ware, "pallet_type_id": i["pallet_type_id"]})

    # -- LOAD: nested load of the root, exact replay, one APPLIED operation, goods leave once --
    def load(self) -> None:
        live = self.live
        composition = live.composition(self.root)
        body = loading_body(self.tag, self.root, composition, self.t["transport_task_id"], self.inputs)
        result = live.send("t.load", "POST", "/api/transport/loading/confirm", body)
        live.replay_equal("t.load")
        moved = live.one("select nvl(sum(BASE_QTY),0) from RRL_EVENTS where OPERATION_ID=:o", o=body["operation_id"])
        expected = -(Decimal(live.s["measurements"]["manual_net_kg"]) + Decimal(c0190.EA_QTY))
        if Decimal(str(moved)) != expected:
            raise RunnerStop(f"LOAD_GOODS_EVENTS:{moved}!={expected}")
        if live.one("select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'", o=body["operation_id"]) != 1:
            raise RunnerStop("LOAD_NOT_SINGLE_APPLIED")
        self.t.update(load_operation_id=body["operation_id"], load_result=result, loaded_composition=composition)
        # C0190 cleanup integration: after the load only the unpicked halves remain in the pick cells.
        self.t["expected_remainder_after_load"] = {live.s["articles"]["kg"]: live.s["measurements"]["manual_net_kg"], live.s["articles"]["ea"]: c0190.EA_QTY}
        live.save()

    # -- TARE_HANDOVER: a separate driver participant accepts the root tare (not the shared admin) --
    def tare_handover(self) -> None:
        live, i = self.live, self.inputs
        if "driver_user" not in self.t:
            self.t["driver_user"] = "MT28D" + uuid4().hex[:9]; live.save()
        actor = self.t["driver_user"]
        if not live.read("select ID from RUSERS where ID=:a", a=actor):
            secret = secrets.token_hex(24); self.t["driver_secret_set"] = True
            with live.connect() as c:
                q = c.cursor()
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'C0191 synthetic driver',:a,:w,0,1)", a=actor, p=secret, w=self.ware)
                for right in ("tare_accept", "tare_offer", "driver_return_accept"):
                    q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:a,:r)", a=actor, r=right)
                c.commit()
            self.driver_secret = secret
        live.send("t.driver.binding", "PUT", f"/api/transport/driver-bindings/{self.t['driver_id']}", {"user_id": actor, "active": True, "expected_version": 0})
        live.send("t.tare.offer", "POST", "/api/inventory/tare/offer", {"operation_id": f"{self.tag}.T.TARE.OFFER", "task_id": self.t["transport_task_id"], "owner_ware_id": self.ware,
                  "pallet_type_id": i["pallet_type_id"], "condition": "GOOD", "from_kind": "WAREHOUSE", "from_id": str(self.ware), "to_kind": "VEHICLE",
                  "to_id": str(self.t["vehicle_id"]), "quantity": "1", "scan_vehicle": i["vehicle_number"], "booking_operation_ids": [f"{self.tag}.T.TARE.BOOK"]})
        self.send_as(actor, "t.tare.accept", "POST", "/api/inventory/tare/accept", {"operation_id": f"{self.tag}.T.TARE.ACCEPT",
                     "offer_operation_id": f"{self.tag}.T.TARE.OFFER", "accepted_quantity": "1", "scan_vehicle": i["vehicle_number"]})

    def send_as(self, actor: str, key: str, method: str, path: str, body: Any) -> Any:
        """The same journal semantics with another participant's credentials (kept in memory only)."""
        import httpx
        secret = getattr(self, "driver_secret", None) or self.live.one("select PASS from RUSERS where ID=:a", a=actor)
        saved, self.live.http = self.live.http, httpx.Client(auth=(actor, secret), timeout=60)
        try:
            return self.live.send(key, method, path, body)
        finally:
            self.live.http = saved

    # -- DEPART: exact replay; a missing real transport document is an explicit stop, never a synthetic ACK --
    def depart(self) -> None:
        live, task = self.live, self.t["transport_task_id"]
        result = live.send("t.depart", "POST", f"/api/transport/loading/{task}/depart", {"operation_id": f"{self.tag}.DEPART"}, expect=(200, 409))
        if isinstance(result, dict) and "DOCUMENT_NOT_READY" in str(result.get("detail", "")):
            raise RunnerStop("EXTERNAL_TRANSPORT_DOCUMENT_REQUIRED: a real ERP transport document must be READY before departure")
        if not (isinstance(result, dict) and "detail" not in result):
            raise RunnerStop(f"DEPART_REFUSED:{str(result)[:300]}")
        live.replay_equal("t.depart")
        status = live.one("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:o", o=self.t["load_operation_id"])
        if status != "DEPARTED":
            raise RunnerStop(f"LOAD_FACT_NOT_DEPARTED:{status}")
        historical = live.composition(self.root)
        if not historical.get("historical_composition") or historical.get("top_place_count") != 1:
            raise RunnerStop("HISTORICAL_TREE_MISSING")
        self.t["historical_tree"] = historical; live.save()

    # -- STORE_RECEIPT: one recipient accepts the one root pallet by its identifier (PAPER_COUNT, explicit counts) --
    def store_receipt(self) -> None:
        live, i = self.live, self.inputs
        addresses = {r[0] for r in live.read("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:o and ACTIVE_FLAG=1", o=self.t["load_operation_id"])}
        if addresses != {i["store_address"]}:
            raise RunnerStop(f"SINGLE_RECIPIENT_REQUIRED:{sorted(addresses)}")
        if "receiver_user" not in self.t:
            self.t["receiver_user"] = "MT28R" + uuid4().hex[:9]; live.save()
        receiver, group = self.t["receiver_user"], self.t["receiver_user"].upper()
        if not live.read("select ID from RUSERS where ID=:a", a=receiver):
            self.receiver_secret = secrets.token_hex(24)
            with live.connect() as c:
                c.cursor().execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'C0191 synthetic store receiver',:g,0,0)",
                                   a=receiver, p=self.receiver_secret, g=group); c.commit()
        live.send("t.receiver.group", "POST", "/api/admin/rights/groups", {"id": group, "name": "C0191 synthetic store receiver"}, expect=(200, 201))
        live.send("t.receiver.right", "POST", f"/api/admin/rights/groups/{group}/rights", {"right_name": "store_receipt_confirm", "description": "C0191 synthetic"}, expect=(200, 201))
        live.send("t.receiver.assign", "POST", "/api/delivery/store-receipts/receivers", {"store_address": i["store_address"], "username": receiver})
        live.send("t.store.policy", "PUT", "/api/delivery/store-receipts/policy", {"store_address": i["store_address"], "mode": "PAPER_COUNT",
                  "expected_version": i["store_policy_expected_version"]})
        import httpx
        from urllib.parse import urlencode
        secret = getattr(self, "receiver_secret", None) or live.one("select PASS from RUSERS where ID=:a", a=receiver)
        shop = httpx.Client(auth=(receiver, secret), timeout=60)
        r = shop.get(live.api + "/api/delivery/store-receipts/preview?" + urlencode({"load_operation_id": self.t["load_operation_id"], "store_address": i["store_address"]}))
        if r.status_code != 200:
            raise RunnerStop(f"STORE_PREVIEW_FAILED:HTTP{r.status_code}:{r.text[:300]}")
        preview = r.json()
        body = store_receipt_body(self.tag, self.t["load_operation_id"], preview, i, receipt_observations(self.t["loaded_composition"]), self.root)
        self.t["store_preview"] = preview; live.save()
        result = self.send_as_secret(receiver, secret, "t.store.receipt", "POST", "/api/delivery/store-receipts/confirm", body)
        if result.get("status") != "ACCEPTED":
            raise RunnerStop(f"STORE_RECEIPT_NOT_ACCEPTED:{str(result)[:300]}")
        self.t["store_receipt"] = result; live.save()

    def send_as_secret(self, actor: str, secret: str, key: str, method: str, path: str, body: Any) -> Any:
        import httpx
        saved, self.live.http = self.live.http, httpx.Client(auth=(actor, secret), timeout=60)
        try:
            result = self.live.send(key, method, path, body)
            self.live.replay_equal(key)  # the receiver repeats the identical receipt after a lost reply
            return result
        finally:
            self.live.http = saved


def run(live: Any, inputs: dict[str, Any]) -> dict[str, Any]:
    """Root entry point after C0190 TREE; stops at the first unmet prerequisite with its exact reason."""
    flow = MixedTreeTransport(live, inputs)
    try:
        for name, fn in zip(STAGES, (flow.shipment, flow.transport_task, flow.floor_qc_tare, flow.load, flow.tare_handover, flow.depart, flow.store_receipt)):
            flow.stage(name, fn)
    except RunnerStop as stop:
        flow.t["stopped"] = str(stop); live.save()
        return {"stopped": str(stop), "last_verified_stage": flow.t.get("last_verified_stage")}
    return {"status": "STORE_RECEIVED", "last_verified_stage": flow.t.get("last_verified_stage")}
