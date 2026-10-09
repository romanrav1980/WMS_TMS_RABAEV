"""Consume only the quantity physically moved by a replenishment task."""
from decimal import Decimal


def apply_replenishment_reservation(gateway, task: dict, finished: bool, fresh_move: bool, actor: str) -> None:
    state = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if not state or state[0]["state"] != "PREPARED":
        applied = gateway.fetch_all("""
            select m.STOCK_MOVE_ID from RRL_WAREHOUSE_TASK_STOCK_MOVE m
              join RRL_STOCK_OPERATION o on o.OPERATION_ID=m.OPERATION_ID
             where m.TASK_ID=:id and o.STATE='APPLIED' and o.COMMAND_TYPE='TASK_COMPLETE'
        """, {"id": int(task["task_id"])})
        if not applied:
            raise ValueError("Use TASK_COMPLETE before synchronizing reservation coverage")
        # The core moved HARD and unit bindings; legacy consumption would be wrong.
        return
    rows = gateway.fetch_all(
        """select sr.* from RRL_STOCK_RESERVATION sr join RRL_PICK_WAVE_REPLENISH_TASK rt
             on rt.SOURCE_RESERVATION_ID=sr.RESERVATION_ID
           where rt.PICK_WAVE_REPLENISH_TASK_ID=:id for update of sr.QTY""",
        {"id": task["source_task_id"]},
    )
    if len(rows) != 1:
        raise ValueError("Replenishment requires its existing source reservation.")
    reserve = rows[0]
    if not fresh_move:
        # Historical sync recovery does not replay partial consumption.
        if finished and reserve["status"] in {"ACTIVE", "ALLOCATED", "PICKING"}:
            gateway.execute("update RRL_STOCK_RESERVATION set STATUS='CONSUMED',CONSUMED_AT=systimestamp,CONSUMED_BY=:a where RESERVATION_ID=:id",
                            {"id": reserve["reservation_id"], "a": actor[:100]})
        return
    if reserve["status"] not in {"ACTIVE", "ALLOCATED", "PICKING"} or reserve["reservation_kind"] != "HARD":
        raise ValueError("Source reservation is no longer an active hard reservation.")
    if reserve.get("uid_pallet") != (task.get("uid_pallet") or task.get("sscc")) or reserve.get("cell") != task.get("from_cell"):
        raise ValueError("Source reservation identifies another pallet or cell.")
    moved = Decimal(str(task["fact_qty"]))
    remaining = Decimal(str(reserve["qty"])) - moved
    if remaining < 0 or (finished and remaining != 0) or (not finished and remaining <= 0):
        raise ValueError("Reserved quantity and actual/residual replenishment do not agree.")
    if finished:
        gateway.execute("update RRL_STOCK_RESERVATION set STATUS='CONSUMED',CONSUMED_AT=systimestamp,CONSUMED_BY=:a where RESERVATION_ID=:id",
                        {"id": reserve["reservation_id"], "a": actor[:100]})
    else:
        gateway.execute("update RRL_STOCK_RESERVATION set QTY=:q where RESERVATION_ID=:id",
                        {"id": reserve["reservation_id"], "q": remaining})
