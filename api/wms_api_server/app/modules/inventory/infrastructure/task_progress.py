"""Read confirmed facts and outstanding work from the existing task family."""
from decimal import Decimal, localcontext
from typing import Any
from fastapi import HTTPException


def task_progress(gateway: Any, task_id: int) -> dict[str, Any]:
    ancestors = gateway.fetch_all(
        """select * from (select TASK_ID, PARENT_TASK_ID, LEVEL TASK_DEPTH, CONNECT_BY_ISCYCLE IS_CYCLE
             from RRL_WAREHOUSE_TASK
            start with TASK_ID=:task_id
          connect by nocycle prior PARENT_TASK_ID=TASK_ID) where rownum<=101""",
        {"task_id": task_id},
    )
    if not ancestors:
        raise HTTPException(404, detail="Warehouse task not found.")
    if len(ancestors) > 100 or any(row["is_cycle"] for row in ancestors):
        raise HTTPException(409, detail="Task family is inconsistent or exceeds 100 steps.")
    root = max(ancestors, key=lambda row: row["task_depth"])["task_id"]
    rows = gateway.fetch_all(
        """select * from (
             select TASK_ID, PARENT_TASK_ID, STATUS, ASSIGNED_TO, RESOURCE_SESSION_ID,
                    EQUIPMENT_ID, FROM_CELL, TO_CELL, UID_PALLET, SSCC,
                    TO_CHAR(QTY,'FM9999999999999999999999999990D999999999',
                            'NLS_NUMERIC_CHARACTERS=''.,''') QUANTITY,
                    TO_CHAR(FACT_QTY,'FM9999999999999999999999999990D999999999',
                            'NLS_NUMERIC_CHARACTERS=''.,''') FACT_QUANTITY,
                    UNIT_CODE, CONNECT_BY_ISCYCLE IS_CYCLE
               from RRL_WAREHOUSE_TASK
              start with TASK_ID=:root_id
            connect by nocycle prior TASK_ID=PARENT_TASK_ID
        ) where rownum<=101""",
        {"root_id": root},
    )
    if len(rows) > 100 or any(row["is_cycle"] for row in rows):
        raise HTTPException(409, detail="Task family is inconsistent or exceeds 100 steps.")
    units = {row["unit_code"] for row in rows}
    if len(units) != 1:
        raise HTTPException(409, detail="Task family units are inconsistent.")
    if any(row["status"] == "DONE" and row["fact_quantity"] is None for row in rows):
        raise HTTPException(409, detail="Completed task has no confirmed quantity.")
    pending = [row for row in rows if row["status"] not in {"DONE", "CANCELLED"}]
    with localcontext() as context:
        context.prec = 50
        done = sum((Decimal(row["fact_quantity"]) for row in rows
                    if row["status"] == "DONE"), Decimal(0))
        remaining = sum((Decimal(row["quantity"] or "0") for row in pending), Decimal(0))
    pending.sort(key=lambda row: (row["status"] != "IN_PROGRESS", row["task_id"]))
    return {
        "task_id": task_id, "root_task_id": root,
        "confirmed_quantity": format(done, "f"), "remaining_quantity": format(remaining, "f"),
        "unit_code": next(iter(units)), "status": "IN_PROGRESS" if pending else ("CANCELLED" if any(row["status"] == "CANCELLED" for row in rows) else "DONE"),
        "next_task_id": pending[0]["task_id"] if pending else None,
        "tasks": rows,
    }
