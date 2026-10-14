"""Credit eligible old pick stock and unique whole-pallet incoming assignments."""
import json
from decimal import Decimal
from typing import Any
from ..contracts_slotting import SlottingError

FACE_CELLS="""select distinct pf.CELL_CODE from RRL_PICK_FACE pf join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=pf.PICK_FACE_ID
 where pf.WARE_ID=:ware and pf.ACTIVE=1 and a.ACTIVE=1 and a.CASE_PICK_ENABLED=1 and a.ARTICUL=:article
 and(a.VALID_FROM is null or a.VALID_FROM<=sysdate)and(a.VALID_TO is null or a.VALID_TO>=sysdate)"""

def old_stock_credit(cur: Any,ware: int,article: str,line_ids: list[int]) -> tuple[Decimal,list[dict[str,Any]]]:
    selected=json.dumps(line_ids)
    cur.execute("""with owned as(
       select sr.UID_PALLET,sr.CELL,sum(sr.BASE_QTY)QTY,min(sr.RESERVATION_ID)OWNER_ID
       from RRL_STOCK_RESERVATION sr join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=sr.PICK_PLAN_LINE_ID
       where sr.ARTICUL=:article and sr.WARE_ID=:ware and sr.RESERVATION_KIND='HARD'
        and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')and pl.CUSTOMER_ORDER_ROW_ID in(
         select ID from json_table(:lines,'$[*]'columns(ID number path '$')))
       group by sr.UID_PALLET,sr.CELL)
       select r.UID_POLETA,r.CELL,to_char(r.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')P,
        to_char(r.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')H,
        to_char(nvl(o.QTY,0),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')OWNED,
        RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,:ware,0,null,null,'ALLOCATE',o.OWNER_ID,:article)REASON
       from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA left join owned o on o.UID_PALLET=r.UID_POLETA and o.CELL=r.CELL
       where p.ARTICUL=:article and r.CELL in("""+FACE_CELLS+""")and r.REMAIN>0
       order by r.CELL,r.UID_POLETA fetch first 501 rows only""",ware=ware,article=article,lines=selected)
    rows=cur.fetchall()
    if len(rows)>500:raise SlottingError("SLOTTING_STOCK_BOUND_500","Сузьте исходный диапазон")
    detail=[];total=Decimal(0)
    for uid,cell,p,h,owned,reason in rows:
        physical,hard,current=map(Decimal,(p,h,owned))
        if hard<0 or hard>physical or current<0 or current>hard:raise SlottingError("SLOTTING_STOCK_RESERVE_CONFLICT","Нарушен баланс исходного отбора")
        credit=min(physical,physical-hard+current)if reason is None else Decimal(0)
        total+=credit
        detail.append({"pallet_identifier":uid,"cell":cell,"physical":p,"hard":h,
            "in_period_hard":owned,"credit":format(credit,"f"),"eligibility_reason":reason})
    return total,detail

def incoming_stock_credit(cur: Any,ware: int,article: str) -> tuple[Decimal,list[dict[str,Any]]]:
    cur.execute("""select t.TASK_ID,t.UID_PALLET,t.FROM_CELL,t.TO_CELL,t.QTY_MODE,
        to_char(r.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')SOURCE_QTY,
        RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,:ware,0,null,null,'REPLENISH',rt.SOURCE_RESERVATION_ID,:article)REASON
        from RRL_WAREHOUSE_TASK t left join RRL_REMAINS r on r.UID_POLETA=t.UID_PALLET and r.CELL=t.FROM_CELL
        left join RRL_PICK_WAVE_REPLENISH_TASK rt on t.TASK_SOURCE='WAVE' and rt.PICK_WAVE_REPLENISH_TASK_ID=t.SOURCE_TASK_ID and rt.PICK_WAVE_ID=t.SOURCE_DOC_ID
        where t.TO_WARE_ID=:ware and t.TASK_TYPE='REPLENISHMENT'and t.TARGET_ARTICUL=:article
         and t.STATUS in('PLANNED','ASSIGNED','IN_PROGRESS')and t.TO_CELL in("""+FACE_CELLS+""")
        order by t.TASK_ID fetch first 201 rows only""",ware=ware,article=article)
    rows=cur.fetchall()
    if len(rows)>200:raise SlottingError("SLOTTING_INBOUND_BOUND_200","Сузьте назначенные подачи")
    identities=[(row[1],row[2])for row in rows];detail=[];total=Decimal(0)
    for task,uid,source,target,mode,quantity,reason in rows:
        duplicate=identities.count((uid,source))>1
        credit=Decimal(quantity)if not duplicate and reason is None and quantity is not None and mode=="PALLET"else Decimal(0)
        total+=credit
        detail.append({"task_id":task,"pallet_identifier":uid,"source_cell":source,"target_cell":target,
            "credit":format(credit,"f"),"exclusion_reason":"DUPLICATE_SOURCE"if duplicate else reason or("WHOLE_PALLET_SOURCE_REQUIRED"if mode!="PALLET"or quantity is None else None)})
    return total,detail
