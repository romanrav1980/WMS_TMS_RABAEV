from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/shared_arrival_reconciliation.py")
s=p.read_text(encoding="utf-8").replace("from ....transaction_gateway import TransactionGateway","from ....transaction_gateway import TransactionGateway\nfrom fastapi import HTTPException",1)
s+='''

def reconcile_warehouse_arrivals(gateway: TransactionGateway, warehouse: int, actor: str) -> int:
    scope=gateway.fetch_all("""select count(*)ALLOWED from RUSERS u where u.ID=:actor
        and nvl(u.DELETED,0)=0 and(u.WARE_ID=:ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""",
        {"actor":actor,"ware":warehouse})
    if not scope or scope[0]["allowed"]!=1:
        raise HTTPException(403,detail="REPLENISHMENT_CURRENT_WAREHOUSE_REQUIRED")
    waves=gateway.fetch_all("""select distinct rt.PICK_WAVE_ID from RRL_PICK_WAVE_REPLENISH_TASK rt
        join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID
        join RRL_STOCK_RESERVATION sr on sr.RESERVATION_ID=rt.SOURCE_RESERVATION_ID
        where w.WARE_ID=:ware and w.STATUS='LAUNCHED' and rt.STATUS='RELEASED'
         and rt.REPLENISHMENT_QTY_MODE='FULL_PALLET' and sr.CELL=rt.TARGET_CELL_CODE
         and rt.SOURCE_CELL_CODE!=rt.TARGET_CELL_CODE and sr.UID_PALLET=rt.PALLET_UID
        order by rt.PICK_WAVE_ID fetch first 201 rows only""", {"ware":warehouse})
    if len(waves)>200:
        raise HTTPException(409,detail="SHARED_ARRIVAL_WAVE_BOUND_200")
    return sum(reconcile_arrived_sources(gateway,int(row["pick_wave_id"]),actor) for row in waves)
'''
files[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/replenishment_continuation.py")
s=p.read_text(encoding="utf-8")
s=s.replace("from fastapi import HTTPException","from fastapi import HTTPException\nfrom ....transaction_gateway import TransactionGateway\nfrom .shared_arrival_reconciliation import reconcile_warehouse_arrivals",1)
s=s.replace("                entered = True","                entered = True\n                reconcile_warehouse_arrivals(TransactionGateway(cursor),warehouse,actor)",1)
files[str(p)]=s
p=Path("api/wms_api_server/app/modules/resources/infrastructure/wave_task_projection.py")
files[str(p)]=p.read_text(encoding="utf-8").replace("rt.REPLENISHMENT_QTY_MODE!='FULL_PALLET'","nvl(rt.REPLENISHMENT_QTY_MODE,'BASE')!='FULL_PALLET'")
p=Path("scripts/case840_second_arrival.py")
s=p.read_text(encoding="utf-8").replace(":uid",":p_uid").replace(":ware",":p_ware").replace(":dst",":p_dst")
# Only SQL diagnostics used these names; original bound statements containing dst/ware elsewhere
# must preserve their own parameter names. Update diagnostic call only.
s=s.replace('dst=dst,ware=ware,uid=extra)', 'p_dst=dst,p_ware=ware,p_uid=extra)')
# Restore all non-diagnostic :dst binds because they use dst=dst.
s=s.replace('SOURCE_LINE_ID=:pt and CELL=:p_dst','SOURCE_LINE_ID=:pt and CELL=:dst')
files[str(p)]=s
print(json.dumps(files,ensure_ascii=True))
