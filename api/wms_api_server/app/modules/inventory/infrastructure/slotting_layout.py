"""Existing published cells and native volume budget in caller READ ONLY snapshot."""
from decimal import Decimal,localcontext
from typing import Any
import oracledb
from ..contracts_slotting import SlottingError
from .slotting_stock import FACE_CELLS

def range_capacity(cur: Any,ware: int,article: str,additional: str|None) -> dict[str,Any]:
    cur.execute("""select distinct pf.PICK_FACE_ID,pf.CELL_CODE,
        to_char(pf.MAX_VOLUME,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),
        to_char(pf.MAX_WEIGHT,'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']'),
        pf.PICK_ROUTE_ID,pf.PICK_ROUTE_CELL_ID,nvl(rs.MODE_CODE,'LEGACY_ACTIVE')MODE_CODE,rs.APPROVAL_OPERATION_ID
        from RRL_PICK_FACE pf
        left join RRL_PICK_FACE_ARTICUL mapping on mapping.PICK_FACE_ID=pf.PICK_FACE_ID and mapping.ARTICUL=:article and mapping.ACTIVE=1
        left join RRL_PICK_RANGE_STATUS rs on rs.PICK_FACE_ARTICUL_ID=mapping.PICK_FACE_ARTICUL_ID
        where pf.WARE_ID=:ware and pf.ACTIVE=1
        and pf.CELL_CODE in("""+FACE_CELLS+""")
        order by pf.PICK_FACE_ID fetch first 101 rows only""",ware=ware,article=article)
    faces=cur.fetchall()
    if len(faces)>100:raise SlottingError("SLOTTING_FACE_BOUND_100","Сузьте действующий диапазон")
    cells=[row[1]for row in faces];rows=[];known=Decimal(0);complete=True
    with localcontext()as ctx:
        ctx.prec=80
        for face,cell,volume,weight,route,route_cell,mode,approval in faces:
            reason=None;capacity=None
            if cells.count(cell)>1:
                reason="AMBIGUOUS_SHARED_PICK_FACE"
            else:
                try:
                    cur.execute("""select to_char(RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(:cell,:article),
                      'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')from dual""",cell=cell,article=article)
                    value=cur.fetchone()[0]
                    if value is None:reason="VOLUME_CAPACITY_NOT_CONFIGURED"
                    else:capacity=Decimal(value);known+=capacity
                except oracledb.DatabaseError as exc:
                    if not 20800<=getattr(exc.args[0],"code",0)<=20999:raise
                    reason=str(exc.args[0]).split("\n",1)[0]
            cur.execute("""select
                (select count(*)from RRL_REMAINS where CELL=:cell and (REMAIN>0 or HARD_RESERVED_BASE>0)),
                (select count(*)from RRL_WAREHOUSE_TASK where (TO_CELL=:cell or FROM_CELL=:cell)and STATUS not in('DONE','CANCELLED')),
                (select count(*)from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
                    where l.CELL_CODE=:cell and t.STATUS not in('DONE','CANCELLED')and l.PLANNED_QTY>nvl(l.PICKED_QTY,0))
                from dual""",cell=cell)
            stock,tasks,case_lines=cur.fetchone()
            blockers=[]
            if stock:blockers.append("PHYSICAL_STOCK_OR_HARD_RESERVE")
            if tasks:blockers.append("ACTIVE_WAREHOUSE_TASKS")
            if case_lines:blockers.append("UNFINISHED_CASE_LINES")
            if capacity is None:complete=False
            rows.append({"pick_face_id":face,"cell":cell,"range_mode":mode,"current_approval_operation_id":approval,
                "new_replenishment_allowed":mode not in{"DRAINING","CLOSED"},"configured_volume_m3":volume,
                "configured_weight_kg":weight,"pick_route_id":route,"pick_route_cell_id":route_cell,
                "remaining_volume_base_quantity":None if capacity is None else format(capacity,"f"),
                "capacity_refusal":reason,"withdrawal_blockers":blockers,
                "immediate_withdrawal_allowed":not blockers,
                "physical_admission":False})
        shortfall=None if additional is None or not complete else format(max(Decimal(0),Decimal(additional)-known),"f")
    return {"cells":rows,"distinct_cell_count":len(set(cells)),
        "capacity_basis":"CANONICAL_REPLENISHMENT_VOLUME_BUDGET",
        "known_remaining_volume_base_quantity":format(known,"f"),"volume_capacity_complete":complete,
        "additional_quantity_outside_known_volume":shortfall,
        "physical_admission":False,"range_applied":False,
        "missing_admission":["WEIGHT_AND_GEOMETRY","PRODUCT_COMPATIBILITY","ROUTE_AND_COST_COMPARISON","RANGE_APPROVAL"]}
