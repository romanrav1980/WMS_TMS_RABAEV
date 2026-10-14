"""Current wave scope and physical CASE evidence in one read-only snapshot."""
import json
from typing import Any
from fastapi import HTTPException


def assert_wave_view(cur: Any, wave: int, actor: str) -> None:
    import oracledb
    try:
        cur.callproc("RRL_WAVE_EXEC_ACCESS.assert_scope", [wave, actor, "pick_wave_view"])
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if code == 20882:
            raise HTTPException(403, detail="WAVE_CURRENT_WARE_VIEWER_REQUIRED") from exc
        if code == 20886 and "WAVE_IDENTITY_MISSING" in str(exc.args[0]):
            raise HTTPException(404, detail="WAVE_NOT_FOUND") from exc
        raise



def execution_snapshot(gateway: Any, wave: int, actor: str) -> dict[str, Any]:
    with gateway.transaction("Current wave execution READ ONLY") as cur:
        if not getattr(gateway, "transaction_bound", False):
            cur.execute("set transaction read only")
        assert_wave_view(cur, wave, actor)
        cur.execute("select RRL_STOCK_WAVE_FINISH_CMD.snapshot_json(:p_wave) from dual", p_wave=wave)
        raw = cur.fetchone()[0]
        data = json.loads(raw.read() if hasattr(raw, "read") else raw)
        # Native blockers/ready remain authoritative. Historical picked quantity is never physical stock.
        cur.execute("""select ct.CASE_PICK_TASK_ID,ct.STATUS,nvl(ct.PICKED_QTY,0),
            (select count(*) from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID
                where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID and r.REMAIN>0) STOCK_ROWS,
            ct.CONTENT_VERSION,ct.CURRENT_CELL,ct.SSCC,st.PALLET_UID
            from RRL_CASE_PICK_TASK ct left join RRL_SBORKA_PALLETS st on st.ID=ct.LEGACY_SBORKA_PALLET_ID
            where ct.PICK_WAVE_ID=:p_wave
            order by ct.CASE_PICK_TASK_ID fetch first 1201 rows only""", p_wave=wave)
        facts = cur.fetchall()
        if len(facts) > 1200:
            raise HTTPException(409, detail="WAVE_EXECUTION_SNAPSHOT_BOUND_1200")
        cases = {str(int(row[0])): row for row in facts}
        for item in data["items"]:
            if item["kind"] != "CASE":
                continue
            row = cases.get(item["id"])
            if row is None:
                continue
            item["physical_stock_rows"] = int(row[3])
            item["quantity_semantics"] = "HISTORICAL_PICKED"
            item["case_content_version"] = int(row[4])
            item["current_cell"] = row[5]
            item["carrier_identifier"] = row[6]
            item["control_identifier"] = row[7]
            if row[1] == "CANCELLED":
                item["display_reason"] = ("CANCELLED_CASE_STOCK_RECONCILIATION_REQUIRED"
                    if row[3] else "CANCELLED_CASE_DEMAND_REPLAN_REQUIRED")
        cur.execute("select RRL_WAVE_EXEC_ACCESS.deferred_snapshot_json(:p_wave)from dual", p_wave=wave)
        raw = cur.fetchone()[0]
        data["deferred_decision"] = json.loads(raw.read() if hasattr(raw, "read") else raw)
        cur.execute("select RRL_WAVE_EXEC_ACCESS.mixed_snapshot_json(:p_wave)from dual", p_wave=wave)
        raw = cur.fetchone()[0]
        data["mixed_decision"] = json.loads(raw.read() if hasattr(raw, "read") else raw)
        data["physical_stock_changed"] = False
        return data
