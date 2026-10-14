"""Reuse shared packet validation, current warehouse scope and immutable evidence."""
import json
from decimal import Decimal
from typing import Any
import oracledb
from ....oracle_gateway import OracleGateway
from ...platform.public import stock_configuration_transaction, read_oracle_json
from ..contracts_warehouse_scale import WarehouseScaleError, WarehouseScaleConfiguration, WarehouseScalePacket


def scale_error(exc: oracledb.DatabaseError) -> WarehouseScaleError:
    code = exc.args[0].code
    status = 403 if code == 20882 else 409 if 20800 <= code <= 20999 else 503
    return WarehouseScaleError("WAREHOUSE_SCALE_REJECTED" if status < 500 else "WAREHOUSE_SCALE_OUTCOME_UNCERTAIN",
                               str(exc.args[0]).split("\n", 1)[0], status)


class WarehouseScales:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def configure(self, device: str, body: WarehouseScaleConfiguration, actor: str) -> dict[str, Any]:
        capacity, resolution = Decimal(body.capacity_kg), Decimal(body.resolution_kg)
        if not 0 < resolution <= capacity:
            raise WarehouseScaleError("SCALE_POLICY_INVALID", "Positive resolution within capacity required", 422)
        try:
            with stock_configuration_transaction(self.gateway, "Warehouse addressed scale device", actor, "warehouse_settings_edit") as q:
                q.execute("select POLICY_VERSION from RRL_WH_SCALE_DEVICE where DEVICE_ID=:p_device for update", p_device=device)
                old = q.fetchone()
                if (int(old[0]) if old else 0) != body.expected_version:
                    raise WarehouseScaleError("SCALE_DEVICE_VERSION_CONFLICT", "Reload the current scale configuration")
                q.execute("""merge into RRL_WH_SCALE_DEVICE d using(select :p_device DEVICE_ID from dual)s on(d.DEVICE_ID=s.DEVICE_ID)
                    when matched then update set WARE_ID=:p_ware,POST_CELL=:p_cell,SENDER_ID=:p_sender,
                    POLICY_VERSION=POLICY_VERSION+1,ACTIVE_FLAG=:p_active,DEVICE_MODE=:p_mode,MEASUREMENT_BASIS=:p_basis,
                    CAPACITY_KG=:p_capacity,RESOLUTION_KG=:p_resolution,CALIBRATION_REF=:p_ref,
                    CALIBRATED_UNTIL=RRL_SCALE_PACKET_READ.utc_stamp(:p_until),CHANGED_BY=:p_actor,CHANGED_AT=systimestamp
                    when not matched then insert(DEVICE_ID,WARE_ID,POST_CELL,SENDER_ID,POLICY_VERSION,ACTIVE_FLAG,DEVICE_MODE,MEASUREMENT_BASIS,
                    CAPACITY_KG,RESOLUTION_KG,CALIBRATION_REF,CALIBRATED_UNTIL,CHANGED_BY)
                    values(:p_device,:p_ware,:p_cell,:p_sender,1,:p_active,:p_mode,:p_basis,:p_capacity,:p_resolution,:p_ref,
                    RRL_SCALE_PACKET_READ.utc_stamp(:p_until),:p_actor)""",
                    p_device=device,p_ware=body.warehouse_id,p_cell=body.post_cell,p_sender=body.sender_id,p_active=int(body.active),
                    p_mode=body.device_mode,p_basis=body.basis,p_capacity=capacity,p_resolution=resolution,p_ref=body.calibration_ref,
                    p_until=body.calibrated_until,p_actor=actor)
        except oracledb.DatabaseError as exc:
            raise scale_error(exc) from exc
        return {"device_id": device, "device_policy_version": body.expected_version + 1,
                "active": body.active, "device_mode": body.device_mode, "basis": body.basis}

    def capture(self, body: WarehouseScalePacket, actor: str) -> dict[str, Any]:
        wire = json.dumps(body.model_dump(), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        try:
            with self.gateway.transaction("Archive warehouse scale packet outside stock posting") as q:
                inp, out = q.var(oracledb.DB_TYPE_CLOB), q.var(oracledb.DB_TYPE_CLOB)
                inp.setvalue(0, wire)
                q.callproc("RRL_WH_SCALE_API.capture", [inp, actor, out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            raise scale_error(exc) from exc

    def readings(self, task: int, line: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Warehouse scale archive scoped READ ONLY") as q:
                q.execute("set transaction read only")
                q.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, "case_pick_execute"])
                q.execute("""select c.RESULT_JSON,c.CAPTURE_KEY,u.STOCK_OPERATION_ID from(
                    select RESULT_JSON,CAPTURE_KEY,RECEIVED_AT from RRL_WH_SCALE_CAPTURE
                    where CASE_PICK_TASK_ID=:p_task and CASE_PICK_LINE_ID=:p_line
                    order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only)c
                    left join RRL_WH_SCALE_USE u on u.CAPTURE_KEY=c.CAPTURE_KEY
                    order by c.RECEIVED_AT desc,c.CAPTURE_KEY desc""", p_task=task, p_line=line)
                rows = q.fetchall()
                return {"items": [read_oracle_json(row[0]) for row in rows[:50]], "has_older": len(rows) > 50,
                        "use_by_capture": {row[1]: {"operation_id": row[2]} for row in rows[:50] if row[2] is not None}}
        except oracledb.DatabaseError as exc:
            raise scale_error(exc) from exc

    def reading(self, key: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Warehouse scale original scoped READ ONLY") as q:
                q.execute("set transaction read only")
                q.execute("select CASE_PICK_TASK_ID,RESULT_JSON from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:p_key", p_key=key)
                row = q.fetchone()
                if row is None:
                    raise WarehouseScaleError("SCALE_CAPTURE_NOT_FOUND", "Scale capture not found", 404)
                q.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [int(row[0]), actor, "case_pick_execute"])
                return read_oracle_json(row[1])
        except oracledb.DatabaseError as exc:
            raise scale_error(exc) from exc
