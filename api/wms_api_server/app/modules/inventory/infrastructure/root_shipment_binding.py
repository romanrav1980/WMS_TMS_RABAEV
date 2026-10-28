"""C-0193: bind one root HU with several closed CASE children to one existing prepared ST in one metadata transaction.

The HU tree is only read (RRL_STOCK_HU_READ.snapshot_json); no detach/repack. Every CASE of the root gets the same ST, every matching
fulfillment its own CASE composition/version; stock is never written. Idempotency without new tables: one ROOT_SHIPMENT_BOUND event per
CASE with OFFLINE_EVENT_ID '<operation>:<task>' (globally unique index) and the request hash in its payload."""
from __future__ import annotations
import json
from decimal import Decimal
from typing import Any
import oracledb
from ....oracle_gateway import OracleGateway
from ....transaction_gateway import TransactionGateway
from ...platform.public import read_oracle_json
from ..contracts_root_shipment import RootShipmentBindRequest, RootShipmentError
from ..domain.carrier_shipment import assert_matching_composition
from ..domain.fulfillment_fact import physical_composition
from ..domain.root_shipment import assert_tree_matches_carriers, check_fulfillments, check_tasks, request_hash, root_children
from .metadata_transactions import receipt_task_metadata

EVENT = "ROOT_SHIPMENT_BOUND"
CARRIER_ROWS = ("select p.ARTICUL,s.BASE_UOM,to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') "
                "from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID "
                "where h.CASE_PICK_TASK_ID=:id and s.REMAIN>0 order by h.LOT_UID,s.CELL fetch first 201 rows only")
ST_ROWS = ("select r.ARTICUL,to_char(r.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),u.BASE_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE "
           "from RRL_SBORKA_PALLET_ROWS r left join RRL_STOCK_UOM_CONVERSION u on u.ARTICUL=r.ARTICUL and u.INPUT_UOM=r.EI and u.POLICY_VERSION="
           "(select max(p.POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION p where p.ARTICUL=r.ARTICUL and p.INPUT_UOM=r.EI) "
           "where r.PALLET_UID=:p_uid order by r.ID fetch first 201 rows only")


class RootShipmentBinding:
    def __init__(self, gateway: OracleGateway | TransactionGateway) -> None:
        self.gateway = gateway

    def bind(self, request: RootShipmentBindRequest, actor: str) -> dict[str, Any]:
        body, op = request.model_dump(mode="json"), request.operation_id
        digest = request_hash(body, actor)
        with receipt_task_metadata(self.gateway, "Bind one root HU to one existing ST", actor, "case_pick_execute") as cur:
            cur.execute("select ID,WARE_ID,CONDITION,RETURN_SUPPLIER_ID from RRL_SBORKA_PALLETS where PALLET_UID=:p for update", {"p": request.shipment_identifier})
            shipments = cur.fetchmany(2)
            if len(shipments) > 1:
                raise RootShipmentError("ST_AMBIGUOUS")
            if not shipments:
                raise RootShipmentError("ST_NOT_FOUND", 404)
            sid, st_ware, condition, supplier = shipments[0]
            replay = self._replay(cur, op, digest)  # read under the ST lock: concurrent identical requests serialize here
            if replay is not None:
                return replay
            cur.execute("select count(*) from RRL_CASE_PICK_TASK where LEGACY_SBORKA_PALLET_ID=:sid", {"sid": sid})
            if cur.fetchone()[0]:
                raise RootShipmentError("ST_ALREADY_BOUND_TO_ANOTHER_PHYSICAL_ROOT")
            try:
                snapshot = read_oracle_json(cur.callfunc("RRL_STOCK_HU_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [request.scanned_root]))
            except oracledb.DatabaseError as exc:
                raise RootShipmentError("ROOT_NOT_FOUND", 404) from exc
            children = root_children(snapshot, request.scanned_root, request.expected_root_version)
            warehouse = snapshot.get("warehouse")
            if st_ware != warehouse or supplier is not None or (condition or 0) >= 2:
                raise RootShipmentError("ST_WAREHOUSE_OR_STATE_MISMATCH")
            tasks = self._lock_tasks(cur, [c["task"] for c in children])
            check_tasks(tasks, children, warehouse, sid)
            orders = {tasks[c["task"]][0] for c in children}
            cur.execute("select FULFILLMENT_ID,CUSTOMER_ORDER_ID,STATUS,ADDRESS_TEXT from RRL_CUSTOMER_ORDER_FULFILLMENT "
                        "where LEGACY_SBORKA_PALLET_ID=:sid and PALLET_UID=:p order by FULFILLMENT_ID for update", {"sid": sid, "p": request.shipment_identifier})
            fulfillments = check_fulfillments(cur.fetchall(), orders)
            per_child: dict[int, list[tuple]] = {}
            for child in children:
                cur.execute(CARRIER_ROWS, {"id": child["task"]})
                rows = cur.fetchall()
                if not rows:
                    raise RootShipmentError("ROOT_CASE_EMPTY")
                per_child[child["task"]] = rows
            physical = [row for rows in per_child.values() for row in rows]
            assert_tree_matches_carriers(snapshot, physical)
            cur.execute(ST_ROWS, {"p_uid": request.shipment_identifier})
            try:
                assert_matching_composition(physical, cur.fetchall())
            except ValueError as exc:
                raise RootShipmentError("ST_COMPOSITION_DIFFERS_FROM_ROOT", 409, str(exc)) from exc
            return self._write(cur, request, actor, digest, sid, children, tasks, fulfillments, per_child)

    def _replay(self, cur: Any, op: str, digest: str) -> dict[str, Any] | None:
        cur.execute("select PAYLOAD_JSON from RRL_CASE_PICK_EVENT where EVENT_TYPE=:e and substr(OFFLINE_EVENT_ID,1,:n)=:prefix",
                    {"e": EVENT, "n": len(op) + 1, "prefix": op + ":"})
        saved = [read_oracle_json(r[0]) for r in cur.fetchall()]
        if not saved:
            return None
        if any(p.get("request_hash") != digest for p in saved):
            raise RootShipmentError("OPERATION_CONTENT_CONFLICT")
        return dict(saved[0]["result"], idempotent=True)

    def _lock_tasks(self, cur: Any, ids: list[int]) -> dict[int, tuple]:
        if not 1 <= len(ids) <= 200:
            raise RootShipmentError("ROOT_CASE_BOUND_200")
        binds = {f"t{i}": t for i, t in enumerate(ids)}
        cur.execute("select CASE_PICK_TASK_ID,CUSTOMER_ORDER_ID,WARE_ID,SSCC,STATUS,CONTENT_VERSION,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK "
                    "where CASE_PICK_TASK_ID in(" + ",".join(":" + k for k in binds) + ") order by CASE_PICK_TASK_ID for update", binds)
        return {int(r[0]): tuple(r[1:]) for r in cur.fetchall()}

    def _write(self, cur: Any, request: RootShipmentBindRequest, actor: str, digest: str, sid: int, children: list[dict[str, Any]],
               tasks: dict[int, tuple], fulfillments: dict[int, int], per_child: dict[int, list[tuple]]) -> dict[str, Any]:
        cases = []
        for child in children:
            composition, quantity, unit = physical_composition(per_child[child["task"]])
            cases.append({"case_pick_task_id": child["task"], "content_version": child["version"], "fulfillment_id": fulfillments[tasks[child["task"]][0]],
                          "physical_composition": composition, "quantity": quantity, "unit": unit})
        result = {"operation_id": request.operation_id, "root": request.scanned_root, "root_version": request.expected_root_version,
                  "shipment_identifier": request.shipment_identifier, "shipment_id": sid, "status": "BOUND", "cases": cases}
        payload = json.dumps({"operation_id": request.operation_id, "request_hash": digest, "result": result}, separators=(",", ":"))
        for case in cases:
            cur.execute("update RRL_CASE_PICK_TASK set LEGACY_SBORKA_PALLET_ID=:sid,UPDATED_AT=systimestamp,UPDATED_BY=:actor "
                        "where CASE_PICK_TASK_ID=:id and LEGACY_SBORKA_PALLET_ID is null", {"sid": sid, "actor": actor, "id": case["case_pick_task_id"]})
            if cur.rowcount != 1:
                raise RootShipmentError("ROOT_CASE_BINDING_CHANGED")
            cur.setinputsizes(composition_json=oracledb.DB_TYPE_CLOB)
            cur.execute("update RRL_CUSTOMER_ORDER_FULFILLMENT set STATUS='PICKED',FACT_QTY=:qty,FACT_UOM=:unit,FACT_COMPOSITION_JSON=:composition_json,"
                        "PICKED_CASE_TASK_ID=:task_id,PICKED_CONTENT_VERSION=:version,PICKED_AT=systimestamp,PICKED_BY=:actor,UPDATED_AT=sysdate,UPDATED_BY=:actor "
                        "where FULFILLMENT_ID=:fid and STATUS='PLANNED'",
                        {"qty": None if case["quantity"] is None else Decimal(case["quantity"]), "unit": case["unit"],
                         "composition_json": json.dumps(case["physical_composition"], separators=(",", ":")), "task_id": case["case_pick_task_id"],
                         "version": case["content_version"], "actor": actor, "fid": case["fulfillment_id"]})
            if cur.rowcount != 1:
                raise RootShipmentError("ST_FULFILLMENT_CHANGED")
            cur.setinputsizes(event_json=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_CASE_PICK_EVENT(CASE_PICK_EVENT_ID,CASE_PICK_TASK_ID,EVENT_TYPE,OFFLINE_EVENT_ID,PAYLOAD_JSON,CREATED_BY) "
                        "values(RRL_CASE_PICK_EVENT_SQ.nextval,:task_id,:event,:event_id,:event_json,:actor)",
                        {"task_id": case["case_pick_task_id"], "event": EVENT, "event_id": f"{request.operation_id}:{case['case_pick_task_id']}",
                         "event_json": payload, "actor": actor})
        return dict(result, idempotent=False)
