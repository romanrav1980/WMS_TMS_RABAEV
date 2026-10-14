"""Reconcile existing pick-face norms into existing REPLENISHMENT waves and root commands."""
from decimal import Decimal,localcontext
from typing import Any,Callable
from uuid import uuid4
from fastapi import HTTPException
from ..contracts_stock import StockCommand,StockPostingError
from .stock_posting_uow import StockPosting

class MinimaxService:
    def __init__(self,gateway: Any,sync_tasks: Callable[[Any,int,str],None]) -> None:
        self.gateway=gateway
        self.sync_tasks=sync_tasks

    def _snapshot(self,cursor: Any,warehouse: int) -> list[dict[str,Any]]:
        cursor.execute("""select pf.PICK_FACE_ID,pf.CELL_CODE,a.ARTICUL,
            case when exists(select 1 from RRL_REMAINS sr join RRL_PALLETS sp on sp.UID_PALLET=sr.UID_POLETA
             join RRL_CELLS sc on sc.CELL=sr.CELL where sp.ARTICUL=a.ARTICUL and sc.WARE_ID=pf.WARE_ID
              and sr.CELL!=pf.CELL_CODE and sr.REMAIN>sr.HARD_RESERVED_BASE
              and RRL_STOCK_ELIGIBILITY.reason(sr.UID_POLETA,sr.CELL,pf.WARE_ID,0,null,null,'REPLENISH',null,a.ARTICUL) is null)
             then 1 else 0 end HAS_SOURCE,

            (select min(rt.MINIMAX_CYCLE_ID) from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID
                where w.WAVE_NAME='NICORA_MINIMAX' and w.STATUS='LAUNCHED' and rt.ARTICUL=a.ARTICUL and rt.TARGET_CELL_CODE=pf.CELL_CODE
                 and rt.MINIMAX_FINISHED_AT is null and rt.MINIMAX_CYCLE_ID is not null) CYCLE_ID,
            to_char((select max(rt.MINIMAX_TARGET_BASE) from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID
                where w.WAVE_NAME='NICORA_MINIMAX' and w.STATUS='LAUNCHED' and rt.ARTICUL=a.ARTICUL and rt.TARGET_CELL_CODE=pf.CELL_CODE
                 and rt.MINIMAX_FINISHED_AT is null),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') CYCLE_TARGET,

            to_char(coalesce(case when a.USE_ARTICUL_REPLENISH_RULE=1 then ar.MIN_TRIGGER_BOX_QTY end,
                a.MIN_TRIGGER_BOX_QTY)*cv.NUMERATOR/cv.DENOMINATOR,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') BOX_MIN_BASE,
            to_char(a.MIN_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') MIN_BASE,
            to_char(a.MAX_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') MAX_BASE,
            coalesce(case when a.USE_ARTICUL_REPLENISH_RULE=1 then ar.REPLENISHMENT_QTY_MODE end,
                a.REPLENISHMENT_QTY_MODE,'FULL_PALLET') QTY_MODE,
            to_char((select nvl(sum(r.REMAIN),0) from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
                where r.CELL=pf.CELL_CODE and p.ARTICUL=a.ARTICUL),'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_BASE,
            (select count(*) from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.ARTICUL=a.ARTICUL
                and rt.TARGET_CELL_CODE=pf.CELL_CODE and (rt.STATUS not in('DONE','CANCELLED','FAILED') or (rt.STATUS='FAILED' and rt.SOURCE_RESERVATION_ID is null))) OPEN_TASKS,
            to_char(RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(pf.CELL_CODE,a.ARTICUL),
                'TM9','NLS_NUMERIC_CHARACTERS=''.,''') CAPACITY_BASE
            from RRL_PICK_FACE pf join RRL_PICK_FACE_ARTICUL a on a.PICK_FACE_ID=pf.PICK_FACE_ID
            join RRL_CELLS c on c.CELL=pf.CELL_CODE and c.WARE_ID=pf.WARE_ID
            left join RRL_ARTICUL_REPLENISH_RULE ar on ar.ARTICUL=a.ARTICUL and ar.ACTIVE=1
            left join RRL_STOCK_UOM_CONVERSION cv on cv.ARTICUL=a.ARTICUL and cv.INPUT_UOM='BOX'
                and cv.POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=a.ARTICUL and INPUT_UOM='BOX')
            where pf.WARE_ID=:ware and pf.ACTIVE=1 and a.ACTIVE=1
                and trunc(sysdate) between trunc(a.VALID_FROM) and nvl(trunc(a.VALID_TO),date '2999-12-31')
                and nvl(c.BLOCKED_FOR_REMAINS,0)=0 and nvl(c.BLOCKED_FOR_POPOLNENIE,0)=0 and nvl(c.IS_SYSTEM,0)=0
                and coalesce(case when a.USE_ARTICUL_REPLENISH_RULE=1 then ar.REPLENISHMENT_METHOD end,a.REPLENISHMENT_METHOD)='MINIMAX'
            order by pf.PICK_FACE_ID,a.ARTICUL fetch first 201 rows only""",{"ware":warehouse})
        keys=[d[0].lower() for d in cursor.description]
        rows=[dict(zip(keys,row)) for row in cursor.fetchall()]
        if len(rows)>200:raise HTTPException(409,detail="MINIMAX_FACE_BOUND_200")
        seen=set()
        with localcontext() as ctx:
            ctx.prec=96
            for row in rows:
                identity=(row["cell_code"],row["articul"])
                if identity in seen:raise HTTPException(409,detail="MINIMAX_SLOT_AMBIGUOUS")
                seen.add(identity)
                threshold=row["box_min_base"] or row["min_base"]
                physical=Decimal(row["physical_base"])
                capacity=None if row["capacity_base"] is None else Decimal(row["capacity_base"])
                target=None if (row["cycle_target"] or row["max_base"]) is None else Decimal(row["cycle_target"] or row["max_base"])
                if target is None and capacity is not None:target=physical+capacity
                row["target_quantity"]=None if target is None else format(target,"f")
                row["quantity"]="0"
                if threshold is None or target is None:row["reason"]="MIN_MAX_NORM_REQUIRED"
                elif Decimal(threshold)<0 or target<=Decimal(threshold):row["reason"]="MIN_MAX_NORM_INVALID"
                elif row["cycle_id"] and physical>=target:row["reason"]="CYCLE_COMPLETE"
                elif row["open_tasks"]:row["reason"]="EXISTING_REPLENISHMENT"
                elif not row["cycle_id"] and physical>Decimal(threshold):row["reason"]="ABOVE_MINIMUM"
                else:
                    qty=max(Decimal(0),target-physical)
                    if capacity is not None:qty=min(qty,capacity)
                    row["quantity"]=format(qty,"f")
                    row["reason"]="WAIT_FREE_CELL" if qty<=0 else "READY" if row["has_source"] else "WAIT_STOCK"
        return rows

    def preview(self,warehouse: int) -> dict[str,Any]:
        with self.gateway.transaction("Read existing minimax norms") as cursor:
            rows=self._snapshot(cursor,warehouse)
        return {"warehouse":warehouse,"faces":rows,"preview":True}

    def reconcile(self,warehouse: int,actor: str) -> dict[str,Any]:
        # Rare metadata planning owns CONFIG X; quantity effects run after its commit through the root.
        with self.gateway.transaction("Reconcile existing minimax replenishment") as cursor:
            entered=False
            try:
                cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'pick_wave_launch');end;",{"actor":actor});entered=True
                rows=self._snapshot(cursor,warehouse)
                cursor.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WARE_ID=:ware and WAVE_KIND='REPLENISHMENT' and WAVE_NAME='NICORA_MINIMAX' and STATUS='LAUNCHED' order by PICK_WAVE_ID for update",{"ware":warehouse})
                waves=cursor.fetchall()
                if len(waves)>1:raise HTTPException(409,detail="MINIMAX_WAVE_AMBIGUOUS")
                wave=int(waves[0][0]) if waves else None
                ready=[row for row in rows if row["reason"]=="READY"]
                if wave is None and ready:
                    cursor.execute("select RRL_PICK_WAVE_SQ.nextval from dual");wave=int(cursor.fetchone()[0])
                    cursor.execute("""insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WAVE_NAME,WARE_ID,WAVE_KIND,STATUS,CREATED_BY)
                        values(:id,:code,'NICORA_MINIMAX',:ware,'REPLENISHMENT','LAUNCHED',:actor)""",
                        {"id":wave,"code":f"MINIMAX:{warehouse}:{uuid4().hex[:12]}","ware":warehouse,"actor":actor})
                if wave is not None:
                    cursor.execute("""select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:wave
                        and STATUS='FAILED' and SOURCE_RESERVATION_ID is null and WAIT_REASON='No eligible source stock'
                        order by PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""",{"wave":wave})
                    retries=cursor.fetchall()
                    if len(retries)>200:raise HTTPException(409,detail="MINIMAX_RETRY_BOUND_200")
                    retry_rows={(row["articul"],row["cell_code"]) for row in rows if row["has_source"]}
                    for (row_id,) in retries:
                        cursor.execute("select ARTICUL,TARGET_CELL_CODE from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",{"id":row_id})
                        if tuple(cursor.fetchone()) not in retry_rows:continue
                        cursor.execute("""update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='RELEASED',WAIT_REASON=null,
                            RESERVE_OPERATION_ID=:operation,UPDATED_BY=:actor,UPDATED_AT=sysdate where PICK_WAVE_REPLENISH_TASK_ID=:id""",
                            {"id":row_id,"actor":actor,"operation":"MINIMAX.SOURCE:"+uuid4().hex})
                for row in rows:
                    if row["reason"]=="CYCLE_COMPLETE":
                        cursor.execute("""update RRL_PICK_WAVE_REPLENISH_TASK set MINIMAX_FINISHED_AT=systimestamp
                            where MINIMAX_CYCLE_ID=:cycle and MINIMAX_FINISHED_AT is null""",{"cycle":row["cycle_id"]})
                for row in ready:
                    cursor.execute("select RRL_STOCK_MATH.quantity(:qty) from dual",{"qty":row["quantity"]})
                    qty=cursor.fetchone()[0]
                    cursor.execute("select RRL_PICK_WAVE_REPL_SQ.nextval from dual");repl=int(cursor.fetchone()[0])
                    cursor.execute("""insert into RRL_PICK_WAVE_REPLENISH_TASK(PICK_WAVE_REPLENISH_TASK_ID,PICK_WAVE_ID,ARTICUL,
                        TARGET_CELL_CODE,QTY,DEMAND_BASE_QTY,STATUS,REPLENISHMENT_METHOD,REPLENISHMENT_QTY_MODE,CREATED_BY,RESERVE_OPERATION_ID,MINIMAX_CYCLE_ID,MINIMAX_TARGET_BASE)
                        values(:repl,:wave,:article,:cell,:qty,:qty,'RELEASED','MINIMAX',:qty_mode,:actor,:operation,:cycle,:target)""",
                        {"repl":repl,"cycle":row["cycle_id"] or repl,"target":Decimal(row["target_quantity"]),"wave":wave,"article":row["articul"],"cell":row["cell_code"],"qty":qty,"qty_mode":row["qty_mode"],"actor":actor,"operation":"MINIMAX.SOURCE:"+uuid4().hex})
            finally:
                if entered:cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
        if wave is None:return {"warehouse":warehouse,"created":0,"wave_id":None,"faces":rows}
        pending=self.gateway.fetch_all("""select PICK_WAVE_REPLENISH_TASK_ID,RESERVE_OPERATION_ID from RRL_PICK_WAVE_REPLENISH_TASK
            where PICK_WAVE_ID=:wave and SOURCE_RESERVATION_ID is null and STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','WAIT_MINIMAX')
            order by PICK_WAVE_REPLENISH_TASK_ID fetch first 201 rows only""",{"wave":wave})
        if len(pending)>200:raise HTTPException(409,detail="MINIMAX_PENDING_BOUND_200")
        result=[]
        for row in pending:
            row_id=int(row["pick_wave_replenish_task_id"])
            operation=row["reserve_operation_id"]
            if not operation:raise HTTPException(409,detail="MINIMAX_SOURCE_INTENT_MISSING")
            try:
                result.append(StockPosting().post(StockCommand(operation_id=operation,command_type="WAVE_RESERVE_SOURCES",actor=actor,
                    lines=(),source={"wave_id":wave},metadata={"requested_row_ids":[row_id]})))
            except StockPostingError as exc:
                uncertain=exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","CONNECTION_UNUSABLE","LOCK_RETRY_EXHAUSTED"}
                raise HTTPException(503 if uncertain else 409,
                    detail={"code":exc.code,"operation_id":operation,"outcome_confirmed":not uncertain,"retry_same_operation_id":uncertain}) from exc
        self.sync_tasks(self.gateway,wave,actor)
        return {"warehouse":warehouse,"created":len(ready),"wave_id":wave,"faces":rows,"reservation_result":result}
