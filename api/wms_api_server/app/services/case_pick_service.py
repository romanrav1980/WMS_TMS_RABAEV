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
                       nvl(RRL_RECIPIENT_PALLET_POLICY.type_id(wo.CUSTOMER_ID,co.CUSTOMER_STORE_MAP_ID), v_euro_pallet_type_id) PALLET_TYPE_ID
                  from RRL_PICK_WAVE_ORDER wo
                  join RRL_PICK_WAVE w on w.PICK_WAVE_ID = wo.PICK_WAVE_ID
                  join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = wo.CUSTOMER_ORDER_ID
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

    def list_tasks(self, resource_id: int | None = None, scope: str = "mine", status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        from ..modules.resources.public import legacy_case_reads
        return legacy_case_reads(self.gateway).list_tasks(resource_id, scope, status, limit)

    def get_task(self, case_pick_task_id: int) -> dict[str, Any] | None:
        from ..modules.resources.public import legacy_case_reads
        return legacy_case_reads(self.gateway).get_task(case_pick_task_id)

    def _resource_action(self,task_id: int,action: str,request: Any) -> None:
        from ..modules.resources.public import execute_existing_case_action
        execute_existing_case_action(self.gateway,task_id,action,request,
            lambda gateway,*args:type(self)(gateway)._event(*args))

    def claim_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None:
        self._resource_action(case_pick_task_id,"claim_task",request)

    def start_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None:
        self._resource_action(case_pick_task_id,"start_task",request)

    def confirm_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineConfirmRequest) -> dict[str, Any]:
        from ..modules.inventory.public import post_existing_case_pick
        from ..modules.inventory.public import StockPostingError
        try:
            posted = post_existing_case_pick(self.gateway, case_pick_task_id, line_id, request)
        except ValueError as exc:
            raise HTTPException(422, detail={"code": "CASE_COMMAND_INVALID", "message": str(exc)}) from exc
        except StockPostingError as exc:
            uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED", "STOCK_RELEASE_NOT_ACTIVE", "POSTED_CONNECTION_RESET_FAILED"} or exc.oracle_code in (20891, 20892, 20893)
            conflict = exc.code == "OPERATION_CONTENT_CONFLICT" or exc.oracle_code in (20872, 20873) or exc.rule_reason == "OPERATION_CONFLICT"
            status = 503 if uncertain else 403 if exc.oracle_code == 20882 else 409
            raise HTTPException(status, detail={"code": exc.code,
                "operation_id": exc.operation_id, "oracle_code": exc.oracle_code, "rule_reason": exc.rule_reason,
                "outcome_confirmed": not (uncertain or conflict or status == 403), "retry_same_operation_id": uncertain,
                "operation_id_conflict": conflict, "read_before_retry": uncertain or conflict or status == 403}) from exc
        return posted

    def short_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest) -> dict[str, Any]:
        from decimal import Decimal
        from ..modules.resources.public import case_short_report_transaction
        from ..transaction_gateway import TransactionGateway
        with case_short_report_transaction(self.gateway, case_pick_task_id, request.actor) as cursor:
            from ..modules.resources.public import assert_case_task_access
            assert_case_task_access(cursor,case_pick_task_id,request.actor,"case_pick_execute")
            bound = TransactionGateway(cursor)
            bound.fetch_all("select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id for update",
                {"id": case_pick_task_id})
            assert_case_task_access(cursor,case_pick_task_id,request.actor,"case_pick_execute")
            from ..modules.inventory.public import short_report_replay
            replay = short_report_replay(bound, case_pick_task_id, line_id, request)
            if replay is not None:
                return replay
            rows = bound.fetch_all("select to_char(PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') POSTED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:task and CASE_PICK_LINE_ID=:line for update",
                {"task": case_pick_task_id, "line": line_id})
            if not rows:
                raise HTTPException(404, detail="Case line not found")
            from ..modules.resources.public import case_resource_context
            case_resource_context(bound,case_pick_task_id,"REPORT",request)
            confirmed = Decimal(str(rows[0]["posted_qty"] or "0"))
            if Decimal(str(request.picked_qty or 0)) != confirmed:
                raise HTTPException(409, detail={"code": "CASE_SHORT_PICKED_FACT_MUST_BE_POSTED",
                    "message": "Confirm actually picked quantity before reporting the remaining shortage"})
            existing = bound.fetch_all("select OFFLINE_EVENT_ID from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=:id and (STATUS in('CREATED','PENDING_APPROVAL') or RECOVERY_STATE in('WAIT_INVENTORY','WAIT_REPLENISHMENT','READY'))", {"id": line_id})
            if existing and (not request.offline_event_id or existing[0]["offline_event_id"] != request.offline_event_id):
                raise HTTPException(409, detail="A shortage already awaits approval for this line")
            return CasePickService(bound)._short_line_locked(case_pick_task_id, line_id, request, approval_pending=True)

    def _short_line_locked(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest, approval_pending: bool = False) -> dict[str, Any]:
        actor = request.actor or "TSD"
        line = self._line_for_update(case_pick_task_id, line_id)
        from ..modules.inventory.public import short_report_replay
        replay = short_report_replay(self.gateway, case_pick_task_id, line_id, request)
        if replay is not None:
            return replay
        from decimal import Decimal
        exact = self.gateway.fetch_all("select to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') Q from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:id", {"id": line_id})
        planned_qty = Decimal(str(exact[0]["q"] or "0"))
        picked_qty = Decimal(str(request.picked_qty or 0))
        short_qty = Decimal(str(request.short_qty)) if request.short_qty is not None else max(planned_qty - picked_qty, Decimal(0))
        if picked_qty < 0 or short_qty <= 0 or picked_qty + short_qty > planned_qty:
            raise HTTPException(422, detail="Invalid picked/short quantity")
        short_id = self.gateway.call_number_plsql(
            """
            declare
              v_id number;v_sla number:=300;
            begin
              select nvl(max(SHORT_RECOVERY_SLA_SECONDS),300) into v_sla from RRL_CASE_PICK_SETTING
               where WARE_ID=(select WARE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:case_pick_task_id) and ACTIVE=1;
              select RRL_CASE_PICK_SHORT_SQ.nextval into v_id from dual;
              insert into RRL_CASE_PICK_SHORT (
                CASE_PICK_SHORT_ID, PICK_WAVE_ID, CASE_PICK_TASK_ID, CASE_PICK_LINE_ID,
                PICK_WAVE_TASK_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID, ARTICUL, CELL_CODE,
                PLANNED_QTY, PICKED_QTY, SHORT_QTY, REASON_TEXT, STATUS,
                OFFLINE_EVENT_ID, CREATED_AT, CREATED_BY, RECOVERY_DEADLINE_AT
              ) values (
                v_id, :pick_wave_id, :case_pick_task_id, :case_pick_line_id,
                :pick_wave_task_id, :customer_order_id, :customer_id, :articul, :cell_code,
                :planned_qty, :picked_qty, :short_qty, substr(:reason_text, 1, 1000), 'PENDING_APPROVAL',
                substr(:offline_event_id, 1, 100), systimestamp, substr(:actor, 1, 100),systimestamp+numtodsinterval(v_sla,'SECOND')
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
               set STATUS = :line_status,
                   PICKED_QTY = :picked_qty,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_LINE_ID = :line_id
            """,
            {"line_id": line_id, "picked_qty": picked_qty, "actor": actor,
                "line_status": "PARTIAL" if approval_pending else "SHORT_PICKED"},
        )
        self._refresh_task_totals(case_pick_task_id, actor)
        self._event(case_pick_task_id, line_id, "SHORT_CREATED", request, actor)
        return {"case_pick_short_id": short_id, "status": "PENDING_APPROVAL", "short_qty": short_qty}

    def close_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> dict[str, Any]:
        from ..modules.inventory.public import close_existing_case_carrier
        from ..modules.resources.public import assert_case_task_access
        return close_existing_case_carrier(self.gateway,case_pick_task_id,request,assert_case_task_access)


    def transfer_task(self, case_pick_task_id: int, request: CasePickTransferRequest) -> None:
        self._resource_action(case_pick_task_id,"transfer_task",request)

    def list_shorts(self, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        from ..modules.resources.public import legacy_case_reads
        return legacy_case_reads(self.gateway).list_shorts(status, limit)

    def approve_short(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, Any]:
        from ..modules.inventory.public import post_existing_case_short_approval
        posted = post_existing_case_short_approval(self.gateway, short_id, request)
        return posted

    def reject_short(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, str]:
        from ..modules.inventory.public import warehouse_metadata_transaction
        from ..transaction_gateway import TransactionGateway
        with warehouse_metadata_transaction(self.gateway, "CASE shortage rejection", request.actor, "case_pick_short_approve") as cursor:
            bound = TransactionGateway(cursor)
            rows = bound.fetch_all("select STATUS,CASE_PICK_TASK_ID from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:id for update", {"id": short_id})
            if not rows:
                raise HTTPException(404, detail="Shortage not found")
            from ..modules.resources.public import assert_case_task_access
            assert_case_task_access(cursor,rows[0]["case_pick_task_id"],request.actor,"case_pick_short_approve")
            if rows[0]["status"] == "REJECTED":
                return {"status": "REJECTED"}
            if rows[0]["status"] not in ("CREATED", "PENDING_APPROVAL"):
                raise HTTPException(409, detail="The shortage has already been accepted")
            return CasePickService(bound)._reject_short_locked(short_id, request)

    def _reject_short_locked(self, short_id: int, request: CasePickShortDecisionRequest) -> dict[str, str]:
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
                   FINAL_WEIGHT_REQUIRED,TYPE_VERSION,ACTIVE
              from RRL_PALLET_TYPE
              {where_sql}
             order by LOAD_UNIT_CLASS, PALLET_TYPE_CODE
            """
        )

    def upsert_pallet_type(self, request: PalletTypeUpsertRequest) -> int:
        from ..modules.inventory.public import upsert_existing_pallet_type
        return upsert_existing_pallet_type(self.gateway,request)

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

    def _event(self,case_pick_task_id: int | None,line_id: int | None,
               event_type: str,request: Any,actor: str) -> None:
        from ..modules.inventory.public import write_existing_case_event
        write_existing_case_event(self.gateway,case_pick_task_id,line_id,event_type,request,actor)
