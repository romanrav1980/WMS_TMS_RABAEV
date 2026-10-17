"""Reuse dynamic pick-face assignments; metadata routing never changes stock or HARD."""
from decimal import Decimal
from typing import Any
from .alternative_face_binding import bind_alternative_face
from .metadata_transactions import begin_wave_metadata


class AlternativePickFaces:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def route_wave(self, wave_id: int, actor: str) -> int:
        with self.gateway.transaction("Route existing replenishment to a free dynamic pick face") as cursor:
            entered = False
            try:
                entered = begin_wave_metadata(self.gateway, cursor, wave_id, actor)
                cursor.execute("""select w.WARE_ID,w.ROUTE_ID from RRL_PICK_WAVE w
                    where w.PICK_WAVE_ID=:wave and w.STATUS='LAUNCHED' and w.PICK_RELEASED_AT is null""", {"wave": wave_id})
                wave = cursor.fetchone()
                if not wave:
                    return 0
                warehouse, route_id = wave
                self._release_empty(cursor, warehouse, actor)
                cursor.execute("""select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.ARTICUL,rt.TARGET_CELL_CODE,
                        nvl(rt.DEMAND_BASE_QTY,rt.QTY),rt.SOURCE_RESERVATION_ID,rt.PICK_TASK_ID,rt.PALLET_UID
                    from RRL_PICK_WAVE_REPLENISH_TASK rt
                    where rt.PICK_WAVE_ID=:wave and rt.STATUS in('RELEASED','QUEUED','WAIT_FREE_CELL','FAILED')
                      and not exists(select 1 from RRL_WAREHOUSE_TASK wh
                        where wh.TASK_SOURCE='WAVE' and wh.SOURCE_DOC_ID=rt.PICK_WAVE_ID
                          and wh.SOURCE_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID and wh.TASK_TYPE='REPLENISHMENT'
                          and wh.STATUS not in('DONE','CANCELLED'))
                      and not exists(select 1 from RRL_PICK_FACE_ASSIGNMENT a
                        where a.PICK_WAVE_REPLENISH_TASK_ID=rt.PICK_WAVE_REPLENISH_TASK_ID and a.STATUS='ACTIVE')
                    order by rt.PICK_WAVE_REPLENISH_TASK_ID fetch first 51 rows only""", {"wave": wave_id})
                rows = cursor.fetchall()
                if len(rows) > 50:
                    raise ValueError("ALTERNATIVE_FACE_BATCH_BOUND_50")
                changed = 0
                for row_id, article, old_cell, demand, source_reservation, pick_task, pallet in rows:
                    changed += self._route(cursor, wave_id, warehouse, route_id, int(row_id),
                                           article, old_cell, Decimal(str(demand)), source_reservation, actor, pick_task, pallet)
                return changed
            finally:
                if entered:
                    cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")

    def _route(self,cursor: Any,wave_id: int,warehouse: int,route_id: int|None,row_id: int,article: str,old_cell: str,demand: Decimal,source_reservation: int|None,actor: str,pick_task: int|None,pallet: str|None) -> int:
        cursor.execute("select TARGET_CELL_CODE from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id", {"id":row_id})
        if cursor.fetchone()[0] != old_cell:
            return 0
        # Existing planner already groups demand by physical source. Keep owners sharing
        # one physical pallet together; different source pallets may use different faces.
        cursor.execute("""select pt.PICK_TASK_ID,greatest(pt.QTY-nvl(pt.FACT_QTY,0),0)
            from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID
            where wt.PICK_WAVE_ID=:wave and wt.TASK_TYPE='CASE_PICK' and pt.ARTICUL=:article
              and nvl(wt.TARGET_CELL_CODE,wt.SOURCE_CELL_CODE)=:cell
              and pt.STATUS not in('DONE','CANCELLED','FAILED')
              and (:pick_task is null or pt.PALLET_UID=:pallet or pt.PICK_TASK_ID=:pick_task)
            order by pt.PICK_TASK_ID fetch first 201 rows only""",
            {"wave":wave_id,"article":article,"cell":old_cell,"pick_task":pick_task,"pallet":pallet})
        group = cursor.fetchall()
        if len(group)>200:
            raise ValueError("ALTERNATIVE_FACE_OWNER_BOUND_200")
        if not group:
            return 0
        ids = ",".join(str(int(r[0])) for r in group)
        required = sum((Decimal(str(r[1])) for r in group),Decimal(0))
        cursor.execute(f"""select count(*) from RRL_CASE_PICK_LINE l where l.PICK_WAVE_ID=:wave
            and l.PICK_TASK_ID in ({ids}) and nvl(l.PICKED_QTY,0)>0""", {"wave":wave_id})
        if cursor.fetchone()[0]:
            return 0
        cursor.execute(f"""select count(*) from RRL_STOCK_RESERVATION sr where sr.SOURCE_DOC_TYPE='PICK_WAVE'
            and sr.SOURCE_DOC_ID=:wave and sr.SOURCE_LINE_ID in ({ids}) and sr.CELL=:cell
            and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING')""",
            {"wave":wave_id,"cell":old_cell})
        if cursor.fetchone()[0]:
            return 0
        cursor.execute(f"""select count(*) from RRL_WAREHOUSE_TASK wh
            join RRL_PICK_WAVE_REPLENISH_TASK rt on rt.PICK_WAVE_REPLENISH_TASK_ID=wh.SOURCE_TASK_ID
             and rt.PICK_WAVE_ID=wh.SOURCE_DOC_ID
            where wh.TASK_SOURCE='WAVE' and wh.TASK_TYPE='REPLENISHMENT'
              and rt.PICK_WAVE_ID=:wave and rt.PICK_TASK_ID in ({ids})
              and wh.STATUS not in('DONE','CANCELLED')""",{"wave":wave_id})
        if cursor.fetchone()[0]:
            return 0
        # Existing physical free target supply should be reconciled by root, not routed away.
        cursor.execute(f"""select nvl(sum(greatest(r.REMAIN-r.HARD_RESERVED_BASE,0)),0)
            from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
            where r.CELL=:cell and p.ARTICUL=:article and r.REMAIN>r.HARD_RESERVED_BASE
              and RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,:ware,0,
                (select max(MIN_SHELF_LIFE_DAYS) from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:wave and PICK_TASK_ID in ({ids})),
                (select max(MIN_SHELF_LIFE_PERCENT) from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:wave and PICK_TASK_ID in ({ids})),
                'ALLOCATE',null,p.ARTICUL) is null""",{"cell":old_cell,"article":article,"ware":warehouse,"wave":wave_id})
        if Decimal(str(cursor.fetchone()[0]))>=required:
            return 0
        cursor.execute("""select RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(:cell,:article,:repl),
                RRL_STOCK_REPL_CAPACITY.unit_volume(:cell,:article) from dual""",
            {"cell": old_cell, "article": article, "repl": row_id})
        capacity, unit_volume = cursor.fetchone()
        if pick_task is not None and pallet:
            cursor.execute("select nvl(max(REMAIN),0) from RRL_REMAINS where UID_POLETA=:pallet and REMAIN>0",{"pallet":pallet})
            required=max(required,Decimal(str(cursor.fetchone()[0])))
        if capacity is None or Decimal(str(capacity)) >= required:
            return 0
        cursor.execute("""select BASE_UOM from RRL_STOCK_UOM_CONVERSION where ARTICUL=:article
            and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1
            and POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION
                where ARTICUL=:article and INPUT_UOM=BASE_UOM and NUMERATOR=1 and DENOMINATOR=1)""", {"article": article})
        base = cursor.fetchone()[0]
        candidates=self._candidates(cursor,warehouse,route_id,old_cell)
        for face, cell, max_volume, sequence, route_cell, route_sequence in candidates:
            available = Decimal(str(max_volume)) / Decimal(str(unit_volume))
            if available < required:
                continue
            # Empty ordinary dynamic target uses whole-pallet mode. It must fit the actual whole source.
            cursor.execute(f"""select count(*) from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
                join RRL_CELLS c on c.CELL=r.CELL
                where p.ARTICUL=:article and c.WARE_ID=:ware and r.CELL!=:cell and r.REMAIN>0
                  and r.REMAIN<=:capacity and (:pick_task is null or r.UID_POLETA=:pallet)
                  and not exists(select 1 from RRL_STOCK_RESERVATION sr
                    where sr.UID_PALLET=r.UID_POLETA and sr.CELL=r.CELL and sr.RESERVATION_KIND='HARD'
                      and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0
                      and not (sr.SOURCE_DOC_TYPE='PICK_WAVE' and sr.SOURCE_DOC_ID=:wave
                        and sr.RESERVATION_DOMAIN='PICKING' and sr.SOURCE_LINE_ID in ({ids})))
                  and RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,:ware,0,null,null,'REPLENISH',
                    coalesce(cast(:source_res as number),(select min(sr.RESERVATION_ID) from RRL_STOCK_RESERVATION sr
                      where sr.UID_PALLET=r.UID_POLETA and sr.CELL=r.CELL and sr.SOURCE_DOC_TYPE='PICK_WAVE'
                        and sr.SOURCE_DOC_ID=:wave and sr.SOURCE_LINE_ID in ({ids}) and sr.RESERVATION_DOMAIN='PICKING'
                        and sr.RESERVATION_KIND='HARD' and sr.STATUS in('ACTIVE','ALLOCATED','PICKING') and sr.BASE_QTY>0)),:article) is null
                  and rownum=1""",
                {"article":article,"ware":warehouse,"cell":cell,"capacity":available,
                 "pick_task":pick_task,"pallet":pallet,"wave":wave_id,"source_res":source_reservation})
            if not cursor.fetchone()[0]:
                continue
            bind_alternative_face(cursor,wave_id,row_id,article,old_cell,face,cell,route_cell,
                route_sequence,sequence,unit_volume,base,actor,ids,source_reservation)
            return 1
        return 0


    @staticmethod
    def _release_empty(cursor: Any, warehouse: int, actor: str) -> None:
        cursor.execute("""update RRL_PICK_FACE_ASSIGNMENT a set STATUS='RELEASED',RELEASED_AT=sysdate,
            RELEASED_BY=:actor,RELEASE_REASON='Physical slot empty; wave demand completed or closed'
            where a.STATUS='ACTIVE' and rownum<=200 and a.PICK_FACE_ID in(select pf.PICK_FACE_ID from RRL_PICK_FACE pf where pf.WARE_ID=:ware)
              and not exists(select 1 from RRL_REMAINS r where r.CELL=a.CELL_CODE and (r.REMAIN>0 or r.HARD_RESERVED_BASE>0))
              and not exists(select 1 from RRL_WAREHOUSE_TASK t where t.TO_CELL=a.CELL_CODE and t.STATUS in('PLANNED','ASSIGNED','IN_PROGRESS'))
              and not exists(select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.TARGET_CELL_CODE=a.CELL_CODE
                and rt.STATUS not in('DONE','CANCELLED','FAILED'))
              and exists(select 1 from RRL_PICK_WAVE w where w.PICK_WAVE_ID=a.PICK_WAVE_ID
                and (w.STATUS in('DONE','CANCELLED') or not exists(select 1 from RRL_PICK_WAVE_TASK wt
                  join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID where wt.PICK_WAVE_ID=w.PICK_WAVE_ID
                    and pt.ARTICUL=a.ARTICUL and nvl(wt.TARGET_CELL_CODE,wt.SOURCE_CELL_CODE)=a.CELL_CODE
                    and pt.STATUS!='CANCELLED' and pt.QTY>nvl(pt.FACT_QTY,0))))""", {"actor":actor,"ware":warehouse})

    @staticmethod
    def _candidates(cursor: Any,warehouse: int,route_id: int|None,old_cell: str) -> list[tuple[Any,...]]:
        cursor.execute("""select pf.PICK_FACE_ID,pf.CELL_CODE,pf.MAX_VOLUME,pf.PICK_SEQUENCE,
                rc.PICK_ROUTE_CELL_ID,rc.PICK_SEQUENCE ROUTE_SEQUENCE
            from RRL_PICK_FACE pf join RRL_CELLS c on c.CELL=pf.CELL_CODE and c.WARE_ID=pf.WARE_ID
             left join RRL_PICK_ROUTE_CELL rc on rc.PICK_ROUTE_ID=:route_id and rc.CELL_CODE=pf.CELL_CODE and rc.ACTIVE=1
            where pf.WARE_ID=:ware and pf.ACTIVE=1 and pf.CELL_CODE!=:old_cell
              and (pf.PICK_FACE_TYPE='DYNAMIC' or pf.ALLOW_DYNAMIC_ASSIGNMENT=1)
              and pf.MAX_VOLUME>0 and c.OTBOR=1 and nvl(c.IS_SYSTEM,0)=0
              and nvl(c.BLOCKED_FOR_REMAINS,0)=0 and nvl(c.BLOCKED_FOR_POPOLNENIE,0)=0
              and (:route_id is null or rc.PICK_ROUTE_CELL_ID is not null)
              and not exists(select 1 from RRL_PICK_FACE_ARTICUL pfa where pfa.PICK_FACE_ID=pf.PICK_FACE_ID
                and pfa.ACTIVE=1 and (pfa.VALID_FROM is null or pfa.VALID_FROM<=sysdate)
                and (pfa.VALID_TO is null or pfa.VALID_TO>=sysdate))
              and not exists(select 1 from RRL_REMAINS r where r.CELL=pf.CELL_CODE and (r.REMAIN>0 or r.HARD_RESERVED_BASE>0))
              and not exists(select 1 from RRL_PICK_FACE_ASSIGNMENT a where a.CELL_CODE=pf.CELL_CODE and a.STATUS='ACTIVE')
              and not exists(select 1 from RRL_WAREHOUSE_TASK wh where wh.TO_CELL=pf.CELL_CODE and wh.STATUS in('PLANNED','ASSIGNED','IN_PROGRESS'))
              and not exists(select 1 from RRL_PICK_WAVE_REPLENISH_TASK rt where rt.TARGET_CELL_CODE=pf.CELL_CODE
                and rt.STATUS not in('DONE','CANCELLED','FAILED'))
            order by nvl(rc.PICK_SEQUENCE,pf.PICK_SEQUENCE) nulls last,pf.CELL_CODE,pf.PICK_FACE_ID
            fetch first 201 rows only""", {"route_id": route_id, "ware": warehouse, "old_cell": old_cell})
        candidates = cursor.fetchall()
        if len(candidates) > 200:
            raise ValueError("ALTERNATIVE_FACE_CANDIDATE_BOUND_200")
        return candidates
