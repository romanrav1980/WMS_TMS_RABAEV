from typing import Any
from ..contracts_tare import TareError
from .tare_load_recovery import recovery_candidates

class TareAssembly:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def _warehouse(self,ware_id: int,actor: str) -> None:
        rows=self.gateway.fetch_all("select count(*) ALLOWED from RUSERS where ID=:actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN' or WARE_ID=:ware or RRL_HAS_WRIGHT(ID,'tare_manage')=1)",{"ware":ware_id,"actor":actor})
        if rows[0]["allowed"]!=1:raise TareError("TARE_ASSEMBLY_WAREHOUSE_FORBIDDEN","Пользователь не назначен складу",403)



    def recovery_candidates(self,load_operation_id: str,actor: str) -> list[dict[str,Any]]:
        return recovery_candidates(self.gateway,load_operation_id,actor)

    def loaded_bookings(self,ware_id: int,task_id: int,actor: str) -> list[dict[str,Any]]:
        self._warehouse(ware_id,actor)
        return self.gateway.fetch_all("""
            select b.OPERATION_ID,b.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,b.PLACE_KIND,b.PLACE_ID,
                   lf.LOAD_OPERATION_ID,lf.TT_ID,lf.VEHICLE_ID,lf.VEHICLE_NUMBER,lf.STATUS LOAD_STATUS
              from RRL_TARE_BOOK b join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=b.PALLET_TYPE_ID
              join RRL_TT_HU_LOAD_FACT lf on
                    (b.PLACE_KIND='HU' and lf.ROOT_UID=b.PLACE_ID)
                    or(b.PLACE_KIND='CASE' and exists(select 1 from json_table(lf.COMPOSITION_JSON,'$.nodes[*]'columns(CASE_ID number path '$.case_task_id'))node where to_char(node.CASE_ID,'TM9')=b.PLACE_ID))
             where b.OWNER_WARE_ID=:ware and b.STATUS='HELD' and lf.WARE_ID=:ware and lf.TT_ID=:task and lf.STATUS in('LOADED','DEPARTED')
             order by b.PALLET_TYPE_ID,b.PLACE_KIND,b.PLACE_ID fetch first 100 rows only
        """,{"ware":ware_id,"task":task_id})

    def forecast(self,ware_id: int,wave_id: int,actor: str) -> dict[str,Any]:
        self._warehouse(ware_id,actor)
        wave=self.gateway.fetch_all("select PICK_WAVE_ID,STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:wave and WARE_ID=:ware",{"wave":wave_id,"ware":ware_id})
        if not wave:raise TareError("TARE_FORECAST_WAVE_REQUIRED","Волна не принадлежит выбранному складу",409)
        counts=self.gateway.fetch_all("""
            select count(*) CASE_COUNT,
                   sum(case when exists(select 1 from RRL_WMS_HU_LINK h where h.CHILD_CASE_TASK_ID=t.CASE_PICK_TASK_ID and h.ACTIVE_FLAG=1) then 1 else 0 end) NESTED_CASE_COUNT
              from RRL_CASE_PICK_TASK t where t.PICK_WAVE_ID=:wave and t.WARE_ID=:ware and t.STATUS not in('SHIPPED','CANCELLED')
        """,{"wave":wave_id,"ware":ware_id})[0]
        if counts["case_count"]>10000:raise TareError("TARE_FORECAST_WAVE_WINDOW_REQUIRED","Разделите прогноз: в волне более 10000 мест CASE",409)
        rows=self.gateway.fetch_all("""
            with demand as(
             select t.PALLET_TYPE_ID,count(*) CASE_COUNT,
                    sum(case when RRL_TARE_PLANNING.case_booking(t.CASE_PICK_TASK_ID,t.WARE_ID,t.PALLET_TYPE_ID) is null then 1 else 0 end) UNBOOKED_COUNT
               from RRL_CASE_PICK_TASK t where t.PICK_WAVE_ID=:wave and t.WARE_ID=:ware and t.STATUS not in('SHIPPED','CANCELLED')
                and not exists(select 1 from RRL_WMS_HU_LINK h where h.CHILD_CASE_TASK_ID=t.CASE_PICK_TASK_ID and h.ACTIVE_FLAG=1)
              group by t.PALLET_TYPE_ID
            ), expected as(
             select o.PALLET_TYPE_ID,sum(o.QUANTITY) PROPOSED_RETURN_QTY from RRL_TARE_OFFER o
              where o.OWNER_WARE_ID=:ware and o.TO_KIND='WAREHOUSE' and o.TO_ID=to_char(:ware,'TM9') and o.CONDITION_CODE='GOOD'
               and not exists(select 1 from RRL_TARE_ACCEPT a where a.OFFER_OPERATION_ID=o.OPERATION_ID) and not exists(select 1 from RRL_TARE_OFFER_CANCEL c where c.OFFER_OPERATION_ID=o.OPERATION_ID)
              group by o.PALLET_TYPE_ID
            )
            select t.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,nvl(d.CASE_COUNT,0) STANDALONE_CASE_COUNT,
                   nvl(d.UNBOOKED_COUNT,0) UNBOOKED_CASE_COUNT,to_char(a.AVAILABLE_QTY,'TM9') AVAILABLE_QUANTITY,
                   case when a.BALANCE_KEY is null then null else to_char(greatest(nvl(d.UNBOOKED_COUNT,0)-a.AVAILABLE_QTY,0),'TM9') end SHORTAGE_QUANTITY,
                   to_char(nvl(e.PROPOSED_RETURN_QTY,0),'TM9') PROPOSED_RETURN_QUANTITY,
                   case when a.BALANCE_KEY is null then 'OBSERVATION_REQUIRED' else 'OBSERVED' end COUNT_STATE
              from RRL_PALLET_TYPE t left join demand d on d.PALLET_TYPE_ID=t.PALLET_TYPE_ID
               left join RRL_TARE_AVAILABILITY a on a.PALLET_TYPE_ID=t.PALLET_TYPE_ID and a.OWNER_WARE_ID=:ware
               left join expected e on e.PALLET_TYPE_ID=t.PALLET_TYPE_ID
             where t.ACTIVE=1 or d.PALLET_TYPE_ID is not null order by t.PALLET_TYPE_NAME fetch first 100 rows only
        """,{"wave":wave_id,"ware":ware_id})
        return {"warehouse_id":ware_id,"wave_id":wave_id,"wave_status":wave[0]["status"],"types":rows,
                "nested_case_count":counts["nested_case_count"] or 0,"scope":"EXISTING_STANDALONE_CASE",
                "planned_returns_are_available":False,"fullpal_type_assignment_required":True}

    def loss_cases(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        self._warehouse(ware_id,actor)
        return self.gateway.fetch_all("""
            select c.OPERATION_ID,c.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,c.CONDITION_CODE,
                   to_char(c.QUANTITY,'TM9') QUANTITY,c.REASON_TEXT,c.DECISION_REFERENCE,c.ACTOR,c.CREATED_AT,b.CUSTODIAN_KIND,b.CUSTODIAN_ID,c.SOURCE_CLAIM_ID,c.TRANSPORT_TASK_ID,
                   d.OPERATION_ID DECISION_OPERATION_ID,d.OUTCOME,d.ACTOR DECIDED_BY
              from RRL_TARE_LOSS_CLAIM c join RRL_TARE_BALANCE b on b.BALANCE_KEY=c.BALANCE_KEY join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID
               left join RRL_TARE_LOSS_DECISION d on d.CLAIM_OPERATION_ID=c.OPERATION_ID
             where c.OWNER_WARE_ID=:ware order by c.CREATED_AT desc,c.OPERATION_ID fetch first 200 rows only
        """,{"ware":ware_id})

    def catalog(self,actor: str) -> dict[str,Any]:
        warehouses=self.gateway.fetch_all("""
            select w.ID,w.NAME from RRL_WARES w where exists(
              select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
               and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=w.ID or RRL_HAS_WRIGHT(u.ID,'tare_manage')=1))
            order by w.NAME,w.ID fetch first 200 rows only
        """,{"actor":actor})
        types=self.gateway.fetch_all("select PALLET_TYPE_ID,PALLET_TYPE_NAME from RRL_PALLET_TYPE where ACTIVE=1 order by PALLET_TYPE_NAME fetch first 100 rows only")
        return {"warehouses":warehouses,"types":types}

    def availability(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        self._warehouse(ware_id,actor)
        return self.gateway.fetch_all("""
            select t.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,t.PALLET_TYPE_CODE,t.ACTIVE,
                   to_char(a.PHYSICAL_QTY,'TM9') PHYSICAL_QUANTITY,
                   to_char(a.ASSEMBLY_QTY,'TM9') ASSEMBLY_QUANTITY,
                   to_char(a.AVAILABLE_QTY,'TM9') AVAILABLE_QUANTITY,to_char(a.LOSS_PENDING_QTY,'TM9') LOSS_PENDING_QUANTITY,a.BALANCE_VERSION,
                   case when a.BALANCE_KEY is null then 'OBSERVATION_REQUIRED' else 'OBSERVED' end COUNT_STATE
              from RRL_PALLET_TYPE t left join RRL_TARE_AVAILABILITY a on a.PALLET_TYPE_ID=t.PALLET_TYPE_ID and a.OWNER_WARE_ID=:ware
             where t.ACTIVE=1 or a.BALANCE_KEY is not null order by t.PALLET_TYPE_NAME fetch first 100 rows only
        """,{"ware":ware_id})

    def bookings(self,ware_id: int,actor: str) -> list[dict[str,Any]]:
        self._warehouse(ware_id,actor)
        return self.gateway.fetch_all("""
            select b.OPERATION_ID,b.PALLET_TYPE_ID,t.PALLET_TYPE_NAME,b.PLACE_KIND,b.PLACE_ID,b.STATUS,b.CREATED_BY,b.CREATED_AT,
                   b.CLOSED_OPERATION_ID,b.CLOSED_BY,b.CLOSED_AT
              from RRL_TARE_BOOK b join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=b.PALLET_TYPE_ID
             where b.OWNER_WARE_ID=:ware order by b.CREATED_AT desc,b.OPERATION_ID desc fetch first 200 rows only
        """,{"ware":ware_id})

def case_snapshot(gateway: Any,task_id: int) -> dict[str,Any]:
    rows=gateway.fetch_all("""
        select t.WARE_ID,t.PALLET_TYPE_ID,p.PALLET_TYPE_NAME,
               to_char(a.AVAILABLE_QTY,'TM9') AVAILABLE_QUANTITY,
               RRL_TARE_PLANNING.case_booking(t.CASE_PICK_TASK_ID,t.WARE_ID,t.PALLET_TYPE_ID) BOOKING_OPERATION_ID,
               case when a.BALANCE_KEY is null then 'OBSERVATION_REQUIRED' else 'OBSERVED' end COUNT_STATE
          from RRL_CASE_PICK_TASK t left join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=t.PALLET_TYPE_ID
          left join RRL_TARE_AVAILABILITY a on a.OWNER_WARE_ID=t.WARE_ID and a.PALLET_TYPE_ID=t.PALLET_TYPE_ID
         where t.CASE_PICK_TASK_ID=:task
    """,{"task":task_id})
    return rows[0] if rows else {}
