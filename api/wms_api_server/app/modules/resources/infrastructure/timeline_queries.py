"""Warehouse-bounded source projections; no second resource or task master."""
from datetime import datetime
from typing import Any
import oracledb
from ..contracts_timeline import TimelineError
from .case_view_scope import view_predicate


def read_rows(cur: Any, sql: str, params: dict[str, Any], limit: int = 2000) -> list[dict[str, Any]]:
    # Python datetime inference uses TIMESTAMP and drops an aware offset. Keep known
    # instants explicit; legacy naive dates retain their existing unresolved policy.
    cur.setinputsizes(**{key: oracledb.DB_TYPE_TIMESTAMP_TZ if isinstance(value, datetime)
                       and value.utcoffset() is not None else None for key, value in params.items()})
    cur.execute(sql, params)
    names = [column[0].lower() for column in cur.description]
    result = [dict(zip(names, row)) for row in cur.fetchall()]
    if len(result) > limit:
        raise TimelineError("RESOURCE_TIMELINE_BOUND_NARROW_WINDOW", 409)
    return result


def resource_rows(cur: Any, warehouse: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    resources = read_rows(cur, """select RESOURCE_ID,RESOURCE_NAME,RESOURCE_CODE,RESOURCE_TYPE,
        RESOURCE_CLASS,EQUIPMENT_ID,USER_ID,STATUS,ZONE_CODE from RRL_RESOURCE
        where WARE_ID=:ware and ACTIVE=1 order by RESOURCE_ID fetch first 501 rows only""", {"ware": warehouse}, 500)
    equipment = read_rows(cur, """select EQUIPMENT_ID,EQUIPMENT_CODE,EQUIPMENT_NAME,EQUIPMENT_TYPE,SERVICE_STATUS,HOME_ZONE_CODE
        from RRL_RESOURCE_EQUIPMENT where WARE_ID=:ware and ACTIVE=1
        order by EQUIPMENT_ID fetch first 501 rows only""", {"ware": warehouse}, 500)
    return resources, equipment


def qualification_rows(cur: Any, warehouse: int) -> list[dict[str, Any]]:
    return read_rows(cur, """select q.RESOURCE_ID,q.TASK_TYPE,
        to_char(q.VALID_FROM,'YYYY-MM-DD"T"HH24:MI:SS.FF6') LEGACY_VALID_FROM,
        to_char(q.VALID_UNTIL,'YYYY-MM-DD"T"HH24:MI:SS.FF6') LEGACY_VALID_UNTIL
        from RRL_RESOURCE_TASK_QUAL q join RRL_RESOURCE r on r.RESOURCE_ID=q.RESOURCE_ID
        where r.WARE_ID=:ware and r.ACTIVE=1 and q.ACTIVE=1 and q.VALID_FROM<=systimestamp
          and(q.VALID_UNTIL is null or q.VALID_UNTIL>systimestamp)
        order by q.RESOURCE_ID,q.TASK_TYPE,q.VALID_FROM fetch first 2001 rows only""", {"ware": warehouse})


def session_rows(cur: Any, warehouse: int) -> list[dict[str, Any]]:
    return read_rows(cur, """select RESOURCE_ID,SESSION_ID,RESOURCE_TYPE,RESOURCE_NAME,RESOURCE_CODE,ZONE_CODE,
        to_char(LAST_HEARTBEAT_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6') LAST_SIGNAL_LOCAL,
        case when LAST_HEARTBEAT_AT>=cast(systimestamp as timestamp)-interval '5'minute then 1 else 0 end SIGNAL_RECENT
        from (select r.RESOURCE_ID,r.RESOURCE_TYPE,r.RESOURCE_NAME,r.RESOURCE_CODE,s.SESSION_ID,s.ZONE_CODE,s.LAST_HEARTBEAT_AT,
            row_number()over(partition by r.RESOURCE_ID order by s.LAST_HEARTBEAT_AT desc nulls last,s.SESSION_ID desc) RN
          from RRL_RESOURCE_SESSION s join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID
          where r.WARE_ID=:ware and r.ACTIVE=1 and s.STATUS='ACTIVE' and s.LOGOUT_AT is null)
        where RN=1 order by RESOURCE_ID fetch first 501 rows only""", {"ware": warehouse}, 500)


def attendance_rows(cur: Any, warehouse: int, start: datetime, finish: datetime) -> list[dict[str, Any]]:
    return read_rows(cur, """select a.PLAN_OPERATION_ID,a.RESOURCE_ID,a.PERSON_ID,
        to_char(a.START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') START_AT,
        to_char(a.FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') FINISH_AT
        from RRL_WORKLOAD_ATTENDANCE a where a.WARE_ID=:ware and a.START_AT<:finish_at and a.FINISH_AT>:start_at
        and not exists(select 1 from RRL_WORKLOAD_ATTEND_CANCEL c where c.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID)
        order by a.START_AT,a.PLAN_OPERATION_ID fetch first 501 rows only""",
        {"ware": warehouse, "start_at": start, "finish_at": finish}, 500)


def task_rows(cur: Any, params: dict[str, Any]) -> list[dict[str, Any]]:
    return read_rows(cur, """select t.TASK_ID,t.TASK_TYPE,t.STATUS,t.RESOURCE_ID,t.EQUIPMENT_ID,t.ASSIGNED_TO,
        t.SOURCE_DOC_TYPE,t.SOURCE_DOC_ID,t.TASK_SOURCE,t.SOURCE_TASK_ID,
        to_char(t.PLANNED_START_AT,'YYYY-MM-DD"T"HH24:MI:SS') PLAN_LOCAL_START,
        to_char(t.PLANNED_FINISH_AT,'YYYY-MM-DD"T"HH24:MI:SS') PLAN_LOCAL_FINISH,
        to_char(t.STARTED_AT_INSTANT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') FACT_START_AT,
        to_char(t.FINISHED_AT_INSTANT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') FACT_FINISH_AT,
        t.LAST_ERROR BLOCKING_REASON from RRL_WAREHOUSE_TASK t
        where (t.FROM_WARE_ID=:ware or t.TO_WARE_ID=:ware)
        and (t.FROM_WARE_ID is null or RRL_ACCESS_API.allowed(:actor,'warehouse_task_view','WAREHOUSE',to_char(t.FROM_WARE_ID))=1)
        and (t.TO_WARE_ID is null or RRL_ACCESS_API.allowed(:actor,'warehouse_task_view','WAREHOUSE',to_char(t.TO_WARE_ID))=1)
        and (t.STATUS not in('DONE','CANCELLED') or (t.STARTED_AT_INSTANT<:finish_at and
          (t.FINISHED_AT_INSTANT is null or t.FINISHED_AT_INSTANT>:start_at)))
        order by t.TASK_ID fetch first 2001 rows only""", params)


def dock_rows(cur: Any, warehouse: int) -> list[dict[str, Any]]:
    return read_rows(cur, """select DOCK,DOCK_IS_BLOCKED from RRL_TT_DOCK where WARE_ID=:ware
        order by ORD,DOCK fetch first 501 rows only""", {"ware": warehouse}, 500)


def case_rows(cur: Any, params: dict[str, Any]) -> list[dict[str, Any]]:
    return read_rows(cur, f"""select t.CASE_PICK_TASK_ID,t.PICK_WAVE_ID,t.STATUS,
        t.ASSIGNED_RESOURCE_ID RESOURCE_ID,t.EQUIPMENT_ID,t.ASSIGNED_TO,t.TOTAL_LINES,t.PICKED_LINES,
        to_char(t.STARTED_AT_INSTANT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') FACT_START_AT,
        to_char(t.DONE_AT,'YYYY-MM-DD"T"HH24:MI:SS') FACT_LOCAL_FINISH,
        t.STARTED_SHIFT_TIME_ZONE from RRL_CASE_PICK_TASK t
        where t.WARE_ID=:ware and {view_predicate('t')} and (t.STATUS not in('DONE','CANCELLED','SHIPPED') or
          (t.STARTED_AT_INSTANT<:finish_at and nvl(t.DONE_AT,nvl(t.CLOSED_AT,t.UPDATED_AT))>=:local_start))
        order by t.CASE_PICK_TASK_ID fetch first 2001 rows only""", params)


def transport_rows(cur: Any, params: dict[str, Any]) -> list[dict[str, Any]]:
    return read_rows(cur, """select o.ID OP_ID,o.TT_ID,o.OPERATION_CODE,t.TRANSPORT,t.DOCK,
        (select max(a.VERSION_NO) from RRL_TT_TIME_APPROVAL a where a.TT_ID=t.ID) APPROVAL_VERSION,
        to_char(o.PLAN_START,'YYYY-MM-DD"T"HH24:MI:SS') PLAN_LOCAL_START,
        to_char(o.PLAN_END,'YYYY-MM-DD"T"HH24:MI:SS') PLAN_LOCAL_FINISH,
        to_char(o.FACT_START,'YYYY-MM-DD"T"HH24:MI:SS') FACT_LOCAL_START,
        to_char(o.FACT_END,'YYYY-MM-DD"T"HH24:MI:SS') FACT_LOCAL_FINISH
        from RRL_TT_OPERATIONS o join RRL_TRANSPORT_TASK t on t.ID=o.TT_ID
        where nvl(t.DELETED,0)=0
        and exists(select 1 from RRL_SBORKA_PALLETS p where p.TRANSTASK_ID=t.ID and p.WARE_ID=:ware)
        and not exists(select 1 from RRL_SBORKA_PALLETS p where p.TRANSTASK_ID=t.ID and
          (p.WARE_ID is null or RRL_ACCESS_API.allowed(:actor,'transport_dispatch_view','WAREHOUSE',to_char(p.WARE_ID))=0))
        and ((o.PLAN_START<:local_finish and (o.PLAN_END>:local_start or o.PLAN_END is null))
          or (o.FACT_START<:local_finish and (o.FACT_END>:local_start or o.FACT_END is null)))
        order by o.TT_ID,o.ORD,o.ID fetch first 2001 rows only""", params)


def loading_rows(cur: Any, params: dict[str, Any]) -> list[dict[str, Any]]:
    return read_rows(cur, """select f.LOAD_OPERATION_ID,f.TT_ID,f.VEHICLE_NUMBER,f.DOCK,f.STATUS,
        f.DEPARTURE_OPERATION_ID,
        to_char(f.LOADED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') LOADED_AT,
        to_char(f.DEPARTED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') DEPARTED_AT
        from RRL_TT_HU_LOAD_FACT f join RRL_STOCK_OPERATION op on op.OPERATION_ID=f.LOAD_OPERATION_ID and op.STATE='APPLIED'
        where f.WARE_ID=:ware
        and((f.LOADED_AT>=:start_at and f.LOADED_AT<:finish_at)
          or(f.DEPARTED_AT>=:start_at and f.DEPARTED_AT<:finish_at))
        and not exists(select 1 from RRL_TT_HU_LOAD_ST ls
          join RRL_SBORKA_PALLETS p on p.ID=ls.SBORKA_PALLET_ID
          where ls.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID and(p.WARE_ID is null
            or RRL_ACCESS_API.allowed(:actor,'transport_dispatch_view','WAREHOUSE',to_char(p.WARE_ID))=0))
        and(not exists(select 1 from RRL_TRADE_SITE site where site.WARE_ID=f.WARE_ID)
          or exists(select 1 from json_table(op.RESOLVED_PLAN_JSON,'$.resources[*]'
            columns(R number path '$.rank'))j where j.R=60))
        and not exists(select 1 from json_table(op.RESOLVED_PLAN_JSON,'$.resources[*]'
          columns(R number path '$.rank',K varchar2(4000)path '$.key_hex'))j
          left join RRL_TRADE_STOCK_ATTR a
            on a.PHYSICAL_UNIT_KEY=lower(substr(utl_raw.cast_to_varchar2(hextoraw(j.K)),-64))
            and rawtohex(RRL_STOCK_LOCK_API.resource_key('UNIT',a.PHYSICAL_UNIT_KEY))=j.K
          where j.R=60 and((a.PHYSICAL_UNIT_KEY is null
            and exists(select 1 from RRL_TRADE_SITE site where site.WARE_ID=f.WARE_ID))
            or(a.PHYSICAL_UNIT_KEY is not null and RRL_TRADE_STOCK_GUARD.owner_allowed(:actor,f.WARE_ID,a.OWNER_ID,0)<>1)))
        order by f.LOADED_AT,f.LOAD_OPERATION_ID fetch first 2001 rows only""", params)
