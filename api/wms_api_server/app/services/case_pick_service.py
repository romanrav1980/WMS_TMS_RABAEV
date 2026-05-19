from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    CasePickLineConfirmRequest,
    CasePickLineShortRequest,
    CasePickShortDecisionRequest,
    CasePickTaskActionRequest,
    CasePickTransferRequest,
    PalletTypeUpsertRequest,
)


def _trim(value: Any, max_len: int, upper: bool = False) -> str | None:
    if value is None:
        return None
    text = str(value).strip()[:max_len]
    if not text:
        return None
    return text.upper() if upper else text


class CasePickService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def ensure_wave_case_pick_tasks(self, pick_wave_id: int, actor: str = "API") -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_count number := 0;
              v_euro_pallet_type_id number;
              v_task_id number;
              v_line_id number;
              v_sscc varchar2(64);
            begin
              select PALLET_TYPE_ID
                into v_euro_pallet_type_id
                from RRL_PALLET_TYPE
               where PALLET_TYPE_CODE = 'EURO_PALLET';

              for r in (
                select wo.PICK_WAVE_ID,
                       wo.PICK_PLAN_ID,
                       wo.CUSTOMER_ORDER_ID,
                       wo.CUSTOMER_ID,
                       co.CUSTOMER_STORE_MAP_ID,
                       w.WARE_ID,
                       nvl(rule.PALLET_TYPE_ID, v_euro_pallet_type_id) PALLET_TYPE_ID
                  from RRL_PICK_WAVE_ORDER wo
                  join RRL_PICK_WAVE w on w.PICK_WAVE_ID = wo.PICK_WAVE_ID
                  join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = wo.CUSTOMER_ORDER_ID
                  left join (
                    select CUSTOMER_ID,
                           CUSTOMER_STORE_MAP_ID,
                           PALLET_TYPE_ID,
                           row_number() over (
                             partition by CUSTOMER_ID, CUSTOMER_STORE_MAP_ID
                             order by IS_DEFAULT desc, CUSTOMER_PALLET_TYPE_RULE_ID
                           ) rn
                      from RRL_CUSTOMER_PALLET_TYPE_RULE
                     where ACTIVE = 1
                       and trunc(sysdate) between VALID_FROM and nvl(VALID_TO, date '2999-12-31')
                  ) rule
                    on rule.CUSTOMER_ID = wo.CUSTOMER_ID
                   and nvl(rule.CUSTOMER_STORE_MAP_ID, -1) = nvl(co.CUSTOMER_STORE_MAP_ID, -1)
                   and rule.rn = 1
                 where wo.PICK_WAVE_ID = :pick_wave_id
                   and wo.STATUS = 'ACTIVE'
                   and exists (
                     select 1
                       from RRL_PICK_WAVE_TASK wt
                       join RRL_PICK_TASK t on t.PICK_TASK_ID = wt.PICK_TASK_ID
                      where wt.PICK_WAVE_ID = wo.PICK_WAVE_ID
                        and t.CUSTOMER_ORDER_ID = wo.CUSTOMER_ORDER_ID
                        and wt.TASK_TYPE = 'CASE_PICK'
                   )
                   and not exists (
                     select 1
                       from RRL_CASE_PICK_TASK cpt
                      where cpt.PICK_WAVE_ID = wo.PICK_WAVE_ID
                        and cpt.CUSTOMER_ORDER_ID = wo.CUSTOMER_ORDER_ID
                        and cpt.PALLET_NO = 1
                   )
              ) loop
                v_task_id := RRL_CASE_PICK_TASK_SQ.nextval;
                v_sscc := 'CP' || to_char(r.PICK_WAVE_ID) || lpad(to_char(v_task_id), 12, '0');
                insert into RRL_CASE_PICK_TASK (
                  CASE_PICK_TASK_ID, PICK_WAVE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ID,
                  CUSTOMER_ID, CUSTOMER_STORE_MAP_ID, SSCC, PALLET_TYPE_ID, PALLET_NO,
                  STATUS, WARE_ID, CREATED_AT, CREATED_BY
                ) values (
                  v_task_id, r.PICK_WAVE_ID, r.PICK_PLAN_ID, r.CUSTOMER_ORDER_ID,
                  r.CUSTOMER_ID, r.CUSTOMER_STORE_MAP_ID, v_sscc, r.PALLET_TYPE_ID, 1,
                  'NEW', r.WARE_ID, systimestamp, substr(:actor, 1, 100)
                );
                v_count := v_count + 1;
              end loop;

              for l in (
                select cpt.CASE_PICK_TASK_ID,
                       wt.PICK_WAVE_ID,
                       wt.PICK_WAVE_TASK_ID,
                       wt.PICK_TASK_ID,
                       t.PICK_PLAN_LINE_ID,
                       t.CUSTOMER_ORDER_ID,
                       t.CUSTOMER_ID,
                       wt.ARTICUL,
                       pl.PRODUCT_NAME,
                       nvl(wt.TARGET_CELL_CODE, wt.SOURCE_CELL_CODE) CELL_CODE,
                       wt.PICK_FACE_ID,
                       wt.PICK_ROUTE_CELL_ID,
                       wt.PICK_SEQUENCE,
                       wt.QTY
                  from RRL_PICK_WAVE_TASK wt
                  join RRL_PICK_TASK t on t.PICK_TASK_ID = wt.PICK_TASK_ID
                  join RRL_CASE_PICK_TASK cpt
                    on cpt.PICK_WAVE_ID = wt.PICK_WAVE_ID
                   and cpt.CUSTOMER_ORDER_ID = t.CUSTOMER_ORDER_ID
                   and cpt.PALLET_NO = 1
                  left join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID = t.PICK_PLAN_LINE_ID
                 where wt.PICK_WAVE_ID = :pick_wave_id
                   and wt.TASK_TYPE = 'CASE_PICK'
                   and not exists (
                     select 1
                       from RRL_CASE_PICK_LINE x
                      where x.CASE_PICK_TASK_ID = cpt.CASE_PICK_TASK_ID
                        and x.PICK_WAVE_TASK_ID = wt.PICK_WAVE_TASK_ID
                   )
                 order by wt.PICK_SEQUENCE nulls last, wt.PICK_WAVE_TASK_ID
              ) loop
                v_line_id := RRL_CASE_PICK_LINE_SQ.nextval;
                insert into RRL_CASE_PICK_LINE (
                  CASE_PICK_LINE_ID, CASE_PICK_TASK_ID, PICK_WAVE_ID, PICK_WAVE_TASK_ID,
                  PICK_TASK_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
                  ARTICUL, PRODUCT_NAME, CELL_CODE, PICK_FACE_ID, PICK_ROUTE_CELL_ID,
                  PICK_SEQUENCE, PLANNED_QTY, STATUS, REQUIRED_SCAN_MODE, CREATED_AT, CREATED_BY
                ) values (
                  v_line_id, l.CASE_PICK_TASK_ID, l.PICK_WAVE_ID, l.PICK_WAVE_TASK_ID,
                  l.PICK_TASK_ID, l.PICK_PLAN_LINE_ID, l.CUSTOMER_ORDER_ID, l.CUSTOMER_ID,
                  l.ARTICUL, l.PRODUCT_NAME, l.CELL_CODE, l.PICK_FACE_ID, l.PICK_ROUTE_CELL_ID,
                  l.PICK_SEQUENCE, l.QTY, 'NEW', 'WAREHOUSE_SETTING', systimestamp, substr(:actor, 1, 100)
                );
                update RRL_PICK_WAVE_TASK
                   set CASE_PICK_TASK_ID = l.CASE_PICK_TASK_ID,
                       CASE_PICK_LINE_ID = v_line_id
                 where PICK_WAVE_TASK_ID = l.PICK_WAVE_TASK_ID;
                update RRL_PICK_TASK
                   set CASE_PICK_TASK_ID = l.CASE_PICK_TASK_ID,
                       CASE_PICK_LINE_ID = v_line_id
                 where PICK_TASK_ID = l.PICK_TASK_ID;
              end loop;

              merge into RRL_CASE_PICK_TASK d
              using (
                select CASE_PICK_TASK_ID,
                       count(*) TOTAL_LINES,
                       sum(PLANNED_QTY) PLANNED_QTY
                  from RRL_CASE_PICK_LINE
                 where PICK_WAVE_ID = :pick_wave_id
                 group by CASE_PICK_TASK_ID
              ) s
              on (d.CASE_PICK_TASK_ID = s.CASE_PICK_TASK_ID)
              when matched then update set
                d.TOTAL_LINES = s.TOTAL_LINES,
                d.PLANNED_QTY = s.PLANNED_QTY,
                d.UPDATED_AT = systimestamp,
                d.UPDATED_BY = substr(:actor, 1, 100);

              :result := v_count;
            end;
            """,
            {"pick_wave_id": pick_wave_id, "actor": actor},
        )

    def list_tasks(
        self,
        resource_id: int | None = None,
        scope: str = "mine",
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = ["1 = 1"]
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if status:
            conditions.append("t.STATUS = :status")
            params["status"] = status.upper()
        else:
            conditions.append("t.STATUS not in ('READY_TO_SHIP', 'CANCELLED')")
        if scope == "mine":
            if resource_id is not None:
                conditions.append("(t.ASSIGNED_RESOURCE_ID = :resource_id or t.ASSIGNED_RESOURCE_ID is null)")
                params["resource_id"] = resource_id
            else:
                conditions.append("t.ASSIGNED_RESOURCE_ID is null")
        elif scope == "free":
            conditions.append("t.ASSIGNED_RESOURCE_ID is null")
        where_sql = " and ".join(conditions)
        return self.gateway.fetch_all(
            f"""
            with task_route as (
              select l.CASE_PICK_TASK_ID,
                     min(pr.ROUTE_CODE) keep (dense_rank first order by nvl(l.PICK_SEQUENCE, 999999), l.CASE_PICK_LINE_ID) ROUTE_CODE,
                     min(pr.ROUTE_NAME) keep (dense_rank first order by nvl(l.PICK_SEQUENCE, 999999), l.CASE_PICK_LINE_ID) ROUTE_NAME,
                     min(rc.ZONE_CODE) keep (dense_rank first order by nvl(l.PICK_SEQUENCE, 999999), l.CASE_PICK_LINE_ID) ZONE_CODE
                from RRL_CASE_PICK_LINE l
                left join RRL_PICK_ROUTE_CELL rc on rc.PICK_ROUTE_CELL_ID = l.PICK_ROUTE_CELL_ID
                left join RRL_PICK_ROUTE pr on pr.PICK_ROUTE_ID = rc.PICK_ROUTE_ID
               group by l.CASE_PICK_TASK_ID
            ),
            task_short as (
              select CASE_PICK_TASK_ID,
                     min(CASE_PICK_SHORT_ID) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_SHORT_ID,
                     min(REASON_TEXT) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_REASON,
                     min(CELL_CODE) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_CELL_CODE,
                     min(CREATED_BY) keep (dense_rank first order by CREATED_AT desc, CASE_PICK_SHORT_ID desc) BLOCKING_CREATED_BY
                from RRL_CASE_PICK_SHORT
               where STATUS in ('CREATED', 'PENDING_APPROVAL')
               group by CASE_PICK_TASK_ID
            ),
            task_event as (
              select CASE_PICK_TASK_ID,
                     min(EVENT_TYPE) keep (dense_rank last order by CREATED_AT, CASE_PICK_EVENT_ID) LAST_EVENT_TYPE,
                     min(MESSAGE_TEXT) keep (dense_rank last order by CREATED_AT, CASE_PICK_EVENT_ID) LAST_EVENT_TEXT,
                     max(CREATED_AT) LAST_EVENT_AT
                from RRL_CASE_PICK_EVENT
               where CASE_PICK_TASK_ID is not null
               group by CASE_PICK_TASK_ID
            ),
            wave_totals as (
              select PICK_WAVE_ID,
                     count(*) ROUTE_PALLET_COUNT,
                     sum(case when STATUS in ('WAIT_CONTROL', 'CONTROL_IN_PROGRESS', 'CONTROLLED', 'READY_TO_SHIP') then 1 else 0 end) ROUTE_DONE_PALLET_COUNT,
                     sum(case when STATUS in ('ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT', 'PICKED') then 1 else 0 end) ROUTE_ACTIVE_PALLET_COUNT,
                     nvl(sum(PLANNED_QTY), 0) ROUTE_PLANNED_QTY,
                     nvl(sum(PICKED_QTY), 0) ROUTE_PICKED_QTY
                from RRL_CASE_PICK_TASK
               where STATUS not in ('CANCELLED', 'FAILED')
               group by PICK_WAVE_ID
            )
            select *
              from (
                select t.CASE_PICK_TASK_ID,
                       t.PICK_WAVE_ID,
                       w.WAVE_CODE,
                       nvl(tr.ROUTE_NAME, tr.ROUTE_CODE) ROUTE,
                       tr.ROUTE_CODE,
                       tr.ROUTE_NAME,
                       t.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       t.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       t.SSCC,
                       pt.PALLET_TYPE_CODE,
                       pt.PALLET_TYPE_NAME,
                       pt.DEFAULT_MAX_CLIENT_PALLETS TROLLEY_PALLET_CAPACITY,
                       t.STATUS,
                       t.ASSIGNED_RESOURCE_ID,
                       t.RESOURCE_SESSION_ID,
                       t.EQUIPMENT_ID,
                       nvl(t.ASSIGNED_TO, nvl(r.RESOURCE_NAME, rs.OPERATOR_USER_ID)) ASSIGNED_TO,
                       r.RESOURCE_CODE,
                       r.RESOURCE_NAME,
                       nvl(e_task.EQUIPMENT_CODE, e_res.EQUIPMENT_CODE) EQUIPMENT_CODE,
                       nvl(e_task.CAPACITY_CLASS, e_res.CAPACITY_CLASS) EQUIPMENT_CAPACITY_CLASS,
                       t.WARE_ID,
                       tr.ZONE_CODE,
                       t.TOTAL_LINES,
                       t.PICKED_LINES,
                       t.PLANNED_QTY,
                       t.PICKED_QTY,
                       round((t.PICKED_QTY / nullif(t.PLANNED_QTY, 0)) * 100) TASK_PROGRESS_PCT,
                       wt.ROUTE_PALLET_COUNT,
                       wt.ROUTE_DONE_PALLET_COUNT,
                       wt.ROUTE_ACTIVE_PALLET_COUNT,
                       wt.ROUTE_PLANNED_QTY,
                       wt.ROUTE_PICKED_QTY,
                       round((wt.ROUTE_PICKED_QTY / nullif(wt.ROUTE_PLANNED_QTY, 0)) * 100) ROUTE_PROGRESS_PCT,
                       ts.BLOCKING_SHORT_ID,
                       ts.BLOCKING_REASON,
                       ts.BLOCKING_CELL_CODE,
                       case
                         when ts.BLOCKING_SHORT_ID is not null then ts.BLOCKING_REASON || case when ts.BLOCKING_CELL_CODE is not null then chr(10) || 'CELL ' || ts.BLOCKING_CELL_CODE end
                         when t.STATUS = 'WAIT_REPLENISHMENT' then 'WAIT_REPLENISHMENT'
                         when t.STATUS = 'SYNC_CONFLICT' then 'SYNC_CONFLICT'
                         else null
                       end PROBLEM,
                       case
                         when te.LAST_EVENT_TYPE is not null then te.LAST_EVENT_TYPE || case when te.LAST_EVENT_TEXT is not null then chr(10) || te.LAST_EVENT_TEXT end
                         when t.CLOSED_AT is not null then 'PALLET_CLOSED'
                         when t.STARTED_AT is not null then 'PICKING_IN_PROGRESS'
                         when t.ASSIGNED_TO is not null then 'TASK_ASSIGNED'
                         else 'TASK_RECEIVED'
                       end LAST_ACTION,
                       te.LAST_EVENT_AT,
                       t.CREATED_AT,
                       t.STARTED_AT,
                       t.CLOSED_AT
                  from RRL_CASE_PICK_TASK t
                  join RRL_PICK_WAVE w on w.PICK_WAVE_ID = t.PICK_WAVE_ID
                  join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = t.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c on c.CUSTOMER_ID = t.CUSTOMER_ID
                  left join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID = t.PALLET_TYPE_ID
                  left join RRL_RESOURCE r on r.RESOURCE_ID = t.ASSIGNED_RESOURCE_ID
                  left join RRL_RESOURCE_SESSION rs on rs.SESSION_ID = t.RESOURCE_SESSION_ID
                  left join RRL_RESOURCE_EQUIPMENT e_task on e_task.EQUIPMENT_ID = t.EQUIPMENT_ID
                  left join RRL_RESOURCE_EQUIPMENT e_res on e_res.EQUIPMENT_ID = r.EQUIPMENT_ID
                  left join task_route tr on tr.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                  left join task_short ts on ts.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                  left join task_event te on te.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                  left join wave_totals wt on wt.PICK_WAVE_ID = t.PICK_WAVE_ID
                 where {where_sql}
                 order by t.STATUS, t.CREATED_AT, t.CASE_PICK_TASK_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_task(self, case_pick_task_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select t.CASE_PICK_TASK_ID,
                   t.PICK_WAVE_ID,
                   w.WAVE_CODE,
                   t.PICK_PLAN_ID,
                   t.CUSTOMER_ORDER_ID,
                   co.ORDER_NO,
                   t.CUSTOMER_ID,
                   c.CUSTOMER_NAME,
                   t.SSCC,
                   pt.PALLET_TYPE_CODE,
                   pt.PALLET_TYPE_NAME,
                   t.STATUS,
                   t.ASSIGNED_RESOURCE_ID,
                   t.RESOURCE_SESSION_ID,
                   t.EQUIPMENT_ID,
                   t.ASSIGNED_TO,
                   t.WARE_ID,
                   t.TOTAL_LINES,
                   t.PICKED_LINES,
                   t.PLANNED_QTY,
                   t.PICKED_QTY,
                   t.CREATED_AT,
                   t.STARTED_AT,
                   t.CLOSED_AT
              from RRL_CASE_PICK_TASK t
              join RRL_PICK_WAVE w on w.PICK_WAVE_ID = t.PICK_WAVE_ID
              join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = t.CUSTOMER_ORDER_ID
              left join RRL_CUSTOMER c on c.CUSTOMER_ID = t.CUSTOMER_ID
              left join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID = t.PALLET_TYPE_ID
             where t.CASE_PICK_TASK_ID = :case_pick_task_id
            """,
            {"case_pick_task_id": case_pick_task_id},
        )
        if not rows:
            return None
        task = rows[0]
        task["lines"] = self.gateway.fetch_all(
            """
            select CASE_PICK_LINE_ID,
                   PICK_WAVE_TASK_ID,
                   PICK_TASK_ID,
                   ARTICUL,
                   PRODUCT_NAME,
                   CELL_CODE,
                   PICK_SEQUENCE,
                   PLANNED_QTY,
                   PICKED_QTY,
                   STATUS,
                   LAST_OFFLINE_EVENT_ID,
                   STARTED_AT,
                   DONE_AT
              from RRL_CASE_PICK_LINE
             where CASE_PICK_TASK_ID = :case_pick_task_id
             order by PICK_SEQUENCE nulls last, CASE_PICK_LINE_ID
            """,
            {"case_pick_task_id": case_pick_task_id},
        )
        return task

    def claim_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None:
        actor = request.actor or "TSD"
        updated = self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK
               set STATUS = case when STATUS = 'NEW' then 'ASSIGNED' else STATUS end,
                   ASSIGNED_RESOURCE_ID = nvl(:resource_id, ASSIGNED_RESOURCE_ID),
                   RESOURCE_SESSION_ID = nvl(:resource_session_id, RESOURCE_SESSION_ID),
                   EQUIPMENT_ID = nvl(:equipment_id, EQUIPMENT_ID),
                   ASSIGNED_TO = substr(:actor, 1, 100),
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_TASK_ID = :case_pick_task_id
               and STATUS in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT')
               and (ASSIGNED_RESOURCE_ID is null or ASSIGNED_RESOURCE_ID = :resource_id or :resource_id is null)
            """,
            {
                "case_pick_task_id": case_pick_task_id,
                "resource_id": request.resource_id,
                "resource_session_id": request.resource_session_id,
                "equipment_id": request.equipment_id,
                "actor": actor,
            },
        )
        if updated == 0:
            raise HTTPException(status_code=409, detail="Case-pick task cannot be claimed.")
        self._event(case_pick_task_id, None, "CLAIMED", request, actor)

    def start_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None:
        actor = request.actor or "TSD"
        self.claim_task(case_pick_task_id, request)
        self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK
               set STATUS = 'IN_PROGRESS',
                   STARTED_AT = nvl(STARTED_AT, systimestamp),
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_TASK_ID = :case_pick_task_id
               and STATUS in ('ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT')
            """,
            {"case_pick_task_id": case_pick_task_id, "actor": actor},
        )
        self._event(case_pick_task_id, None, "STARTED", request, actor)

    def confirm_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineConfirmRequest) -> dict[str, Any]:
        actor = request.actor or "TSD"
        line = self._line_for_update(case_pick_task_id, line_id)
        if request.offline_event_id and self._offline_event_exists(request.offline_event_id):
            return {"status": line.get("status"), "idempotent": True}
        self._validate_line_scan(line, request)
        planned_qty = float(line.get("planned_qty") or 0)
        fact_qty = float(request.fact_qty if request.fact_qty is not None else planned_qty)
        if fact_qty <= 0:
            raise HTTPException(status_code=400, detail="fact_qty must be greater than zero.")
        if fact_qty > planned_qty:
            raise HTTPException(status_code=409, detail="fact_qty cannot exceed planned quantity.")
        new_status = "PICKED" if fact_qty >= planned_qty else "PARTIAL"
        self.gateway.execute(
            """
            update RRL_CASE_PICK_LINE
               set STATUS = :status,
                   PICKED_QTY = :fact_qty,
                   LAST_OFFLINE_EVENT_ID = substr(:offline_event_id, 1, 100),
                   STARTED_AT = nvl(STARTED_AT, systimestamp),
                   DONE_AT = case when :status = 'PICKED' then systimestamp else DONE_AT end,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_LINE_ID = :line_id
            """,
            {
                "line_id": line_id,
                "status": new_status,
                "fact_qty": fact_qty,
                "offline_event_id": request.offline_event_id,
                "actor": actor,
            },
        )
        self.gateway.execute(
            """
            update RRL_PICK_TASK
               set STATUS = case when :status = 'PICKED' then 'DONE' else 'IN_PROGRESS' end,
                   FACT_QTY = :fact_qty,
                   DONE_AT = case when :status = 'PICKED' then sysdate else DONE_AT end,
                   DONE_BY = case when :status = 'PICKED' then substr(:actor, 1, 50) else DONE_BY end,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:actor, 1, 50)
             where PICK_TASK_ID = :pick_task_id
            """,
            {"pick_task_id": line.get("pick_task_id"), "status": new_status, "fact_qty": fact_qty, "actor": actor},
        )
        self.gateway.execute(
            """
            update RRL_PICK_WAVE_TASK
               set STATUS = case when :status = 'PICKED' then 'DONE' else 'IN_PROGRESS' end,
                   FACT_QTY = :fact_qty,
                   DONE_AT = case when :status = 'PICKED' then sysdate else DONE_AT end,
                   DONE_BY = case when :status = 'PICKED' then substr(:actor, 1, 50) else DONE_BY end,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:actor, 1, 50)
             where PICK_WAVE_TASK_ID = :pick_wave_task_id
            """,
            {
                "pick_wave_task_id": line.get("pick_wave_task_id"),
                "status": new_status,
                "fact_qty": fact_qty,
                "actor": actor,
            },
        )
        self._refresh_task_totals(case_pick_task_id, actor)
        self._event(case_pick_task_id, line_id, "LINE_CONFIRMED", request, actor)
        return {"status": new_status, "fact_qty": fact_qty}

    def short_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest) -> dict[str, Any]:
        actor = request.actor or "TSD"
        line = self._line_for_update(case_pick_task_id, line_id)
        if request.offline_event_id and self._offline_event_exists(request.offline_event_id):
            return {"status": line.get("status"), "idempotent": True}
        planned_qty = float(line.get("planned_qty") or 0)
        picked_qty = float(request.picked_qty or 0)
        short_qty = float(request.short_qty if request.short_qty is not None else max(planned_qty - picked_qty, 0))
        short_id = self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_CASE_PICK_SHORT_SQ.nextval into v_id from dual;
              insert into RRL_CASE_PICK_SHORT (
                CASE_PICK_SHORT_ID, PICK_WAVE_ID, CASE_PICK_TASK_ID, CASE_PICK_LINE_ID,
                PICK_WAVE_TASK_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID, ARTICUL, CELL_CODE,
                PLANNED_QTY, PICKED_QTY, SHORT_QTY, REASON_TEXT, STATUS,
                OFFLINE_EVENT_ID, CREATED_AT, CREATED_BY
              ) values (
                v_id, :pick_wave_id, :case_pick_task_id, :case_pick_line_id,
                :pick_wave_task_id, :customer_order_id, :customer_id, :articul, :cell_code,
                :planned_qty, :picked_qty, :short_qty, substr(:reason_text, 1, 1000), 'PENDING_APPROVAL',
                substr(:offline_event_id, 1, 100), systimestamp, substr(:actor, 1, 100)
              );
              :result := v_id;
            end;
            """,
            {
                "pick_wave_id": line.get("pick_wave_id"),
                "case_pick_task_id": case_pick_task_id,
                "case_pick_line_id": line_id,
                "pick_wave_task_id": line.get("pick_wave_task_id"),
                "customer_order_id": line.get("customer_order_id"),
                "customer_id": line.get("customer_id"),
                "articul": line.get("articul"),
                "cell_code": line.get("cell_code"),
                "planned_qty": planned_qty,
                "picked_qty": picked_qty,
                "short_qty": short_qty,
                "reason_text": request.reason_text,
                "offline_event_id": request.offline_event_id,
                "actor": actor,
            },
        )
        self.gateway.execute(
            """
            update RRL_CASE_PICK_LINE
               set STATUS = 'SHORT_PICKED',
                   PICKED_QTY = :picked_qty,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_LINE_ID = :line_id
            """,
            {"line_id": line_id, "picked_qty": picked_qty, "actor": actor},
        )
        self._refresh_task_totals(case_pick_task_id, actor)
        self._event(case_pick_task_id, line_id, "SHORT_CREATED", request, actor)
        return {"case_pick_short_id": short_id, "status": "PENDING_APPROVAL", "short_qty": short_qty}

    def close_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> dict[str, Any]:
        actor = request.actor or "TSD"
        self._refresh_task_totals(case_pick_task_id, actor)
        task = self.get_task(case_pick_task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Case-pick task not found.")
        open_lines = [line for line in task["lines"] if line["status"] not in ("PICKED", "SHORT_PICKED", "CANCELLED")]
        if open_lines:
            raise HTTPException(status_code=409, detail="Case-pick task has open lines.")
        new_status = "WAIT_CONTROL"
        self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK
               set STATUS = :status,
                   CLOSED_AT = systimestamp,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_TASK_ID = :case_pick_task_id
            """,
            {"case_pick_task_id": case_pick_task_id, "status": new_status, "actor": actor},
        )
        self._event(case_pick_task_id, None, "CLOSED", request, actor)
        return {"status": new_status}

    def transfer_task(self, case_pick_task_id: int, request: CasePickTransferRequest) -> None:
        actor = request.actor or "SHIFT_LEAD"
        updated = self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK
               set STATUS = case when STATUS = 'NEW' then 'ASSIGNED' else STATUS end,
                   ASSIGNED_RESOURCE_ID = :to_resource_id,
                   RESOURCE_SESSION_ID = :to_resource_session_id,
                   EQUIPMENT_ID = :to_equipment_id,
                   ASSIGNED_TO = substr(:actor, 1, 100),
                   TRANSFERRED_AT = systimestamp,
                   TRANSFERRED_BY = substr(:actor, 1, 100),
                   TRANSFER_REASON = substr(:reason, 1, 1000),
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_TASK_ID = :case_pick_task_id
               and STATUS in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT')
            """,
            {
                "case_pick_task_id": case_pick_task_id,
                "to_resource_id": request.to_resource_id,
                "to_resource_session_id": request.to_resource_session_id,
                "to_equipment_id": request.to_equipment_id,
                "reason": request.reason,
                "actor": actor,
            },
        )
        if updated == 0:
            raise HTTPException(status_code=409, detail="Case-pick task cannot be transferred.")
        self._event(case_pick_task_id, None, "TRANSFERRED", request, actor)

    def list_shorts(self, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if status:
            conditions.append("s.STATUS = :status")
            params["status"] = status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select s.CASE_PICK_SHORT_ID,
                       s.PICK_WAVE_ID,
                       s.CASE_PICK_TASK_ID,
                       s.CASE_PICK_LINE_ID,
                       s.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       s.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       s.ARTICUL,
                       s.CELL_CODE,
                       s.PLANNED_QTY,
                       s.PICKED_QTY,
                       s.SHORT_QTY,
                       s.REASON_CODE,
                       s.REASON_TEXT,
                       s.STATUS,
                       s.INVENTORY_TASK_ID,
                       s.CREATED_AT,
                       s.CREATED_BY,
                       s.APPROVED_AT,
                       s.APPROVED_BY
                  from RRL_CASE_PICK_SHORT s
                  left join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = s.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c on c.CUSTOMER_ID = s.CUSTOMER_ID
                  {where_sql}
                 order by s.CREATED_AT desc, s.CASE_PICK_SHORT_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def approve_short(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, Any]:
        actor = request.actor or "SHIFT_LEAD"
        rows = self.gateway.fetch_all(
            """
            select s.*, t.WARE_ID
              from RRL_CASE_PICK_SHORT s
              left join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID = s.CASE_PICK_TASK_ID
             where s.CASE_PICK_SHORT_ID = :short_id
            """,
            {"short_id": short_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Case-pick short not found.")
        short = rows[0]
        if short.get("status") == "ACCEPTED":
            return {"status": "ACCEPTED", "inventory_task_id": short.get("inventory_task_id")}
        inventory_task_id = self._create_inventory_task_for_short(short, actor)
        self.gateway.execute(
            """
            update RRL_CASE_PICK_SHORT
               set STATUS = 'ACCEPTED',
                   INVENTORY_TASK_ID = nvl(:inventory_task_id, INVENTORY_TASK_ID),
                   APPROVED_AT = systimestamp,
                   APPROVED_BY = substr(:actor, 1, 100),
                   REASON_TEXT = substr(nvl(:reason_text, REASON_TEXT), 1, 1000)
             where CASE_PICK_SHORT_ID = :short_id
            """,
            {
                "short_id": short_id,
                "inventory_task_id": inventory_task_id,
                "reason_text": request.reason_text,
                "actor": actor,
            },
        )
        return {"status": "ACCEPTED", "inventory_task_id": inventory_task_id}

    def reject_short(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, str]:
        actor = request.actor or "SHIFT_LEAD"
        self.gateway.execute(
            """
            update RRL_CASE_PICK_SHORT
               set STATUS = 'REJECTED',
                   APPROVED_AT = systimestamp,
                   APPROVED_BY = substr(:actor, 1, 100),
                   REASON_TEXT = substr(nvl(:reason_text, REASON_TEXT), 1, 1000)
             where CASE_PICK_SHORT_ID = :short_id
               and STATUS in ('CREATED', 'PENDING_APPROVAL')
            """,
            {"short_id": short_id, "reason_text": request.reason_text, "actor": actor},
        )
        return {"status": "REJECTED"}

    def list_pallet_types(self, active_only: int | None = None) -> list[dict[str, Any]]:
        where_sql = " where ACTIVE = 1" if active_only else ""
        return self.gateway.fetch_all(
            f"""
            select PALLET_TYPE_ID,
                   PALLET_TYPE_CODE,
                   PALLET_TYPE_NAME,
                   LOAD_UNIT_CLASS,
                   DEFAULT_VOLUME_M3,
                   DEFAULT_WEIGHT_KG,
                   LENGTH_MM,
                   WIDTH_MM,
                   HEIGHT_MM,
                   DEFAULT_MAX_CLIENT_PALLETS,
                   ACTIVE
              from RRL_PALLET_TYPE
              {where_sql}
             order by LOAD_UNIT_CLASS, PALLET_TYPE_CODE
            """
        )

    def upsert_pallet_type(self, request: PalletTypeUpsertRequest) -> int:
        actor = request.updated_by or "API"
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number := :pallet_type_id;
            begin
              if v_id is null then
                begin
                  select PALLET_TYPE_ID into v_id
                    from RRL_PALLET_TYPE
                   where PALLET_TYPE_CODE = upper(:pallet_type_code);
                exception
                  when no_data_found then
                    select RRL_PALLET_TYPE_SQ.nextval into v_id from dual;
                end;
              end if;
              merge into RRL_PALLET_TYPE d
              using (select v_id PALLET_TYPE_ID from dual) s
              on (d.PALLET_TYPE_ID = s.PALLET_TYPE_ID)
              when matched then update set
                d.PALLET_TYPE_CODE = upper(:pallet_type_code),
                d.PALLET_TYPE_NAME = :pallet_type_name,
                d.LOAD_UNIT_CLASS = upper(:load_unit_class),
                d.DEFAULT_VOLUME_M3 = :default_volume_m3,
                d.DEFAULT_WEIGHT_KG = :default_weight_kg,
                d.LENGTH_MM = :length_mm,
                d.WIDTH_MM = :width_mm,
                d.HEIGHT_MM = :height_mm,
                d.DEFAULT_MAX_CLIENT_PALLETS = :default_max_client_pallets,
                d.ACTIVE = :active,
                d.UPDATED_AT = systimestamp,
                d.UPDATED_BY = substr(:actor, 1, 100)
              when not matched then insert (
                PALLET_TYPE_ID, PALLET_TYPE_CODE, PALLET_TYPE_NAME, LOAD_UNIT_CLASS,
                DEFAULT_VOLUME_M3, DEFAULT_WEIGHT_KG, LENGTH_MM, WIDTH_MM, HEIGHT_MM,
                DEFAULT_MAX_CLIENT_PALLETS, ACTIVE, CREATED_AT, CREATED_BY
              ) values (
                v_id, upper(:pallet_type_code), :pallet_type_name, upper(:load_unit_class),
                :default_volume_m3, :default_weight_kg, :length_mm, :width_mm, :height_mm,
                :default_max_client_pallets, :active, systimestamp, substr(:actor, 1, 100)
              );
              :result := v_id;
            end;
            """,
            {
                **request.model_dump(),
                "pallet_type_code": _trim(request.pallet_type_code, 50, upper=True),
                "pallet_type_name": _trim(request.pallet_type_name, 160),
                "load_unit_class": _trim(request.load_unit_class, 20, upper=True),
                "actor": actor,
            },
        )

    def _line_for_update(self, case_pick_task_id: int, line_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_CASE_PICK_LINE
             where CASE_PICK_TASK_ID = :case_pick_task_id
               and CASE_PICK_LINE_ID = :line_id
            """,
            {"case_pick_task_id": case_pick_task_id, "line_id": line_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Case-pick line not found.")
        line = rows[0]
        if line.get("status") in ("PICKED", "CANCELLED", "FAILED"):
            raise HTTPException(status_code=409, detail="Case-pick line is closed.")
        return line

    def _validate_line_scan(self, line: dict[str, Any], request: CasePickLineConfirmRequest) -> None:
        if request.scan_cell and line.get("cell_code"):
            if request.scan_cell.upper() != str(line["cell_code"]).upper():
                raise HTTPException(status_code=409, detail="Scanned pick cell does not match line.")
        if request.scan_product:
            scanned = request.scan_product.upper()
            expected = str(line.get("articul") or "").upper()
            if scanned != expected:
                raise HTTPException(
                    status_code=409,
                    detail="Scanned product/barcode does not match line. Shift lead must fix master data before picking.",
                )

    def _refresh_task_totals(self, case_pick_task_id: int, actor: str) -> None:
        self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK t
               set (TOTAL_LINES, PICKED_LINES, PLANNED_QTY, PICKED_QTY) = (
                     select count(*),
                            sum(case when STATUS in ('PICKED', 'SHORT_PICKED', 'CANCELLED') then 1 else 0 end),
                            nvl(sum(PLANNED_QTY), 0),
                            nvl(sum(PICKED_QTY), 0)
                       from RRL_CASE_PICK_LINE l
                      where l.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                   ),
                   STATUS = case
                     when exists (
                       select 1 from RRL_CASE_PICK_LINE l
                        where l.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                          and l.STATUS = 'WAIT_REPLENISHMENT'
                     ) then 'WAIT_REPLENISHMENT'
                     when exists (
                       select 1 from RRL_CASE_PICK_LINE l
                        where l.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                          and l.STATUS in ('PARTIAL', 'SHORT_PICKED')
                     ) then 'PARTIAL'
                     when not exists (
                       select 1 from RRL_CASE_PICK_LINE l
                        where l.CASE_PICK_TASK_ID = t.CASE_PICK_TASK_ID
                          and l.STATUS not in ('PICKED', 'SHORT_PICKED', 'CANCELLED')
                     ) then 'PICKED'
                     when t.STATUS in ('NEW', 'ASSIGNED') then t.STATUS
                     else 'IN_PROGRESS'
                   end,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where t.CASE_PICK_TASK_ID = :case_pick_task_id
            """,
            {"case_pick_task_id": case_pick_task_id, "actor": actor},
        )

    def _create_inventory_task_for_short(self, short: dict[str, Any], actor: str) -> int | None:
        settings = self.gateway.fetch_all(
            """
            select AUTO_INVENTORY_ON_SHORT,
                   INVENTORY_RESOURCE_TYPE
              from RRL_CASE_PICK_SETTING
             where WARE_ID = :ware_id
               and ACTIVE = 1
            """,
            {"ware_id": short.get("ware_id")},
        )
        if settings and int(settings[0].get("auto_inventory_on_short") or 0) == 0:
            return None
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_INVENTORY_TASK_SQ.nextval into v_id from dual;
              insert into RRL_INVENTORY_TASK (
                INVENTORY_TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_DOC_TYPE, SOURCE_DOC_ID,
                STATUS, WARE_ID, CELL_CODE, ARTICUL, PLANNED_QTY,
                ASSIGNED_RESOURCE_TYPE, CREATED_AT, CREATED_BY
              ) values (
                v_id, 'INVENTORY_CHECK', 'CASE_PICK_SHORT', 'CASE_PICK_SHORT', :short_id,
                'NEW', :ware_id, :cell_code, :articul, :planned_qty,
                :resource_type, systimestamp, substr(:actor, 1, 100)
              );
              :result := v_id;
            end;
            """,
            {
                "short_id": short.get("case_pick_short_id"),
                "ware_id": short.get("ware_id"),
                "cell_code": short.get("cell_code"),
                "articul": short.get("articul"),
                "planned_qty": short.get("planned_qty"),
                "resource_type": (settings[0].get("inventory_resource_type") if settings else "INVENTORY"),
                "actor": actor,
            },
        )

    def _offline_event_exists(self, offline_event_id: str) -> bool:
        rows = self.gateway.fetch_all(
            """
            select 1
              from RRL_CASE_PICK_EVENT
             where OFFLINE_EVENT_ID = :offline_event_id
               and rownum = 1
            """,
            {"offline_event_id": offline_event_id[:100]},
        )
        return bool(rows)

    def _event(
        self,
        case_pick_task_id: int | None,
        line_id: int | None,
        event_type: str,
        request: Any,
        actor: str,
    ) -> None:
        data = request.model_dump() if hasattr(request, "model_dump") else {}
        self.gateway.execute_plsql(
            """
            begin
              insert into RRL_CASE_PICK_EVENT (
                CASE_PICK_EVENT_ID, CASE_PICK_TASK_ID, CASE_PICK_LINE_ID, EVENT_TYPE,
                OFFLINE_EVENT_ID, RESOURCE_ID, RESOURCE_SESSION_ID, EQUIPMENT_ID,
                MESSAGE_TEXT, PAYLOAD_JSON, CREATED_AT, CREATED_BY
              ) values (
                RRL_CASE_PICK_EVENT_SQ.nextval, :case_pick_task_id, :case_pick_line_id, :event_type,
                substr(:offline_event_id, 1, 100), :resource_id, :resource_session_id, :equipment_id,
                substr(:message_text, 1, 1000), :payload_json, systimestamp, substr(:actor, 1, 100)
              );
            exception
              when dup_val_on_index then
                null;
            end;
            """,
            {
                "case_pick_task_id": case_pick_task_id,
                "case_pick_line_id": line_id,
                "event_type": event_type,
                "offline_event_id": data.get("offline_event_id"),
                "resource_id": data.get("resource_id") or data.get("to_resource_id"),
                "resource_session_id": data.get("resource_session_id") or data.get("to_resource_session_id"),
                "equipment_id": data.get("equipment_id") or data.get("to_equipment_id"),
                "message_text": data.get("reason") or data.get("reason_text"),
                "payload_json": str(data)[:3900],
                "actor": actor,
            },
        )
