"""Current physical remainder admission for the existing SAP putaway replan."""
from decimal import Decimal
from typing import Any
import oracledb


def admit_current_source(cur: oracledb.Cursor, task_id: int, task: tuple[Any, ...], receipt: dict[str, Any]) -> dict[str, Any]:
    cur.execute("select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION from RRL_REMAINS where CELL=:p_cell and UID_POLETA=:p_uid for update",
                p_cell=task[1],p_uid=task[0])
    rows=cur.fetchall()
    cur.execute("select POSTED_BASE_QTY,STOCK_BASE_UOM from RRL_SAP_PALLET_RECEIPT where UID_PALLET=:p_uid",p_uid=task[0])
    admitted=cur.fetchone()
    if len(rows)!=1 or not admitted or admitted[0] is None or admitted[1] is None:
        raise ValueError("Current physical source and original admitted base quantity are required")
    physical,hard,base,version=rows[0]
    original=Decimal(str(admitted[0]));current=Decimal(str(physical));task_quantity=Decimal(str(task[6]))
    if current<=0 or current>original or base!=admitted[1]:
        raise ValueError("Current pallet remainder is unavailable or exceeds the original receipt")
    result={"original_received_base_quantity":str(original),"current_base_quantity":str(current),
            "current_stock_version":int(version),"current_task_quantity":str(task_quantity)}
    direct_operation=None
    if str(task[7]or"").startswith("DIRECT_PICK_BY_LINE:"):
        direct_operation=str(task[7]).removeprefix("DIRECT_PICK_BY_LINE:")
    if current==original and direct_operation is None:
        return result
    if direct_operation is None:
        raise ValueError("Pallet source quantity changed; cannot replan blindly")
    cur.execute("""select count(*)from RRL_STOCK_OPERATION op,
        json_table(op.RESOLVED_PLAN_JSON,'$.domain.direct_putaway_holds[*]'columns(
            TASK_ID number path '$.task_id',UID_VALUE varchar2(150)path '$.uid',
            CELL_VALUE varchar2(60)path '$.cell')) held
        where op.OPERATION_ID=:p_operation and op.STATE='APPLIED'and op.COMMAND_TYPE='WAVE_LAUNCH'
          and held.TASK_ID=:p_task and held.UID_VALUE=:p_uid and held.CELL_VALUE=:p_cell""",
        p_operation=direct_operation,p_task=task_id,p_uid=task[0],p_cell=task[1])
    if cur.fetchone()[0]!=1:
        raise ValueError("Original native DIRECT handoff proof is required")
    cur.execute("""select count(*)from RRL_PICK_RESERVATION pr join RRL_PICK_TASK pt on pt.PICK_TASK_ID=pr.PICK_TASK_ID
        where pr.PALLET_UID=:p_uid and pr.SOURCE_CELL_CODE=:p_cell and pr.RESERVATION_STATUS='ACTIVE'
          and pt.STATUS in('NEW','ASSIGNED','IN_PROGRESS')""",p_uid=task[0],p_cell=task[1])
    if Decimal(str(hard))!=0 or cur.fetchone()[0]>0:
        raise ValueError("Finish or cancel current direct allocations before placing the remainder")
    cur.execute("""select NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION
        where ARTICUL=:p_article and INPUT_UOM=(select UNIT_CODE from RRL_WAREHOUSE_TASK where TASK_ID=:p_task)
          and BASE_UOM=:p_base order by POLICY_VERSION desc fetch first 1 row only""",
        p_article=receipt["material"],p_task=task_id,p_base=base)
    ratio=cur.fetchone()
    if not ratio or Decimal(str(ratio[0]))!=1 or Decimal(str(ratio[1]))!=1:
        raise ValueError("Direct remainder replan requires the original exact base unit")
    result.update(current_task_quantity=str(current),direct_handoff_operation_id=direct_operation)
    return result
