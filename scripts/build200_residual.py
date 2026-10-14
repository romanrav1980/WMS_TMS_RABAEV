from pathlib import Path
import json,hashlib
out={};p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving.py");s=p.read_text(encoding="utf-8")
folder=Path("db/migrations/2026-10-11_ni042_direct_residual")
out[str(folder/"000_before_receiving.py")]=s
out[str(folder/"checkpoint.json")]=json.dumps({"increment":"200-direct-residual-putaway","before_receiving_sha256":hashlib.sha256(s.encode()).hexdigest(),"recovery":"Scoped existing metadata replan behavior; original before source preserved; no physical data rewrite"},indent=2)
s=s.replace("select UID_PALLET,FROM_CELL,FROM_WARE_ID,STATUS,TASK_SOURCE,SOURCE_DOC_ID from RRL_WAREHOUSE_TASK where TASK_ID=:t for update","select UID_PALLET,FROM_CELL,FROM_WARE_ID,STATUS,TASK_SOURCE,SOURCE_DOC_ID,QTY,LAST_ERROR from RRL_WAREHOUSE_TASK where TASK_ID=:t for update",1)
a=s.index("            cur.execute(\"select to_char(REMAIN")
b=s.index('            cur.execute("update RRL_WAREHOUSE_TASK set STATUS=',a)
s=s[:a]+'''            from .receipt_replan_source import admit_current_source
            source_proof = admit_current_source(cur,task_id,task,receipt)
'''+s[b:]
old="set STATUS='PLANNED',TO_CELL=:c,TO_CELL_SLOT_ID=:s,"
new="set STATUS='PLANNED',QTY=:q,TO_CELL=:c,TO_CELL_SLOT_ID=:s,"
assert old in s;s=s.replace(old,new,1)
s=s.replace("'t': task_id, 'c': placement['cell'], 's': placement['slot_id']})","'t': task_id, 'q': source_proof['current_task_quantity'], 'c': placement['cell'], 's': placement['slot_id']})",1)
s=s.replace("'replanned_by': actor, 'idempotent': False}","'replanned_by': actor, 'idempotent': False, **source_proof}",1)
out[str(p)]=s
out["api/wms_api_server/app/modules/inventory/infrastructure/receipt_replan_source.py"]='''"""Current physical remainder admission for the existing SAP putaway replan."""
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
'''
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8")
old="message(`Задание ${v.task_id}: новый адрес ${v.placement.cell}.`)"
new="message(`Задание ${v.task_id}: новый адрес ${v.placement.cell}. Количество к размещению: ${v.current_task_quantity ?? 'по заданию'}.`)"
assert old in s;out[str(p)]=s.replace(old,new)
out["wiki/database/nicora_ni042_direct_residual_design_20261011.md"]="""# NI04.2: размещение остатка после DIRECT
200 existing metadata replan may accept current original-source physical remainder only with original applied native WAVE_LAUNCH direct_putaway_holds proof/task UID/cell/current warehouse and scanned pallet/source. Original received base quantity preserved; physical P/H current stock version separate. No HARD or active direct task/projection allowed. Exact task base unit1:1; positive current quantity<=original admitted. Old unrelated changed-source refusal preserved. Existing cancelled putaway task becomes PLANNED with current qty and original source docs, old idempotent replan journal/outbox/slot placement reused. No stock effect until existing TASK_COMPLETE; actual outgoing placement quantity must be remainder. Metadata CONFIG X serializes against stock admission.
"""
for path,line in[("wiki/index.md","- [Проект размещения DIRECT-остатка](database/nicora_ni042_direct_residual_design_20261011.md):200 existing replan/current exact remainder/native handoff proof/no active allocations."),
("wiki/log.md","2026-10-11:200 design existing SAP putaway replan accepts proven current DIRECT remainder only; original receipt retained/current P-H/version checked, no hard/pending allocations, same metadata owner/task/slot/outbox; no new stock engine.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
