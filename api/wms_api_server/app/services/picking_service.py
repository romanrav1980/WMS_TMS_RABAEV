from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    ArticulReplenishmentRuleUpsertRequest,
    PickFaceArticulUpsertRequest,
    PickFaceUpsertRequest,
    PickRouteCellUpsertRequest,
    PickRouteUpsertRequest,
    PickTaskCompleteRequest,
    PickWaveActionRequest,
    PickWaveAddPlanRequest,
    PickWaveCreateRequest,
    PickWaveStagingReleaseRequest,
    PickingPlanCreateRequest,
)
from .case_pick_service import CasePickService


class PickingService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def create_plan(self, request: PickingPlanCreateRequest) -> int:
        from ..modules.inventory.public import create_existing_pick_plan
        return create_existing_pick_plan(self.gateway, request)

    def cancel_plan(self, pick_plan_id: int, updated_by: str | None = None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PICKING_API.cancel_plan(
                p_pick_plan_id => :pick_plan_id,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"pick_plan_id": pick_plan_id, "updated_by": updated_by},
        )

    def create_wave(self, request: PickWaveCreateRequest) -> int:
        from ..modules.inventory.public import create_existing_wave
        return create_existing_wave(self.gateway, request)

    def add_wave_plan(self, pick_wave_id: int, request: PickWaveAddPlanRequest) -> None:
        from ..modules.inventory.public import add_existing_wave_plan
        return add_existing_wave_plan(self.gateway, pick_wave_id, request)

    def preview_wave(self, pick_wave_id: int, request: PickWaveActionRequest) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PICK_WAVE_API.preview_wave(
                p_pick_wave_id => :pick_wave_id,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": request.updated_by},
        )

    def _post_wave_command(self, command: str, wave_id: int, request: PickWaveActionRequest) -> bool:
        from ..modules.inventory.public import StockCommand, StockPostingError
        from ..modules.inventory.public import StockPosting
        from ..modules.inventory.public import require_active_stock_release
        require_active_stock_release(self.gateway,request.operation_id)
        if not request.operation_id:
            raise HTTPException(422, detail={"code": "OPERATION_ID_REQUIRED"})
        source = {"wave_id": wave_id} if command == "WAVE_LAUNCH" else {"document_type": "PICK_WAVE", "document_id": wave_id}
        metadata = {} if command == "WAVE_LAUNCH" else {"reason": request.reason or "Wave reservations released", "only_cancelled_replenishment": 0, "reservation_kind": None}
        try:
            StockPosting().post(StockCommand(operation_id=request.operation_id, command_type=command,
                actor=request.updated_by, lines=(), source=source, metadata=metadata))
        except StockPostingError as exc:
            raise HTTPException(409, detail={"code": exc.code, "operation_id": exc.operation_id,
                "oracle_code": exc.oracle_code, "retry_same_operation_id": True}) from exc
        return True

    def launch_wave(self, pick_wave_id: int, request: PickWaveActionRequest) -> None:
        if self._post_wave_command("WAVE_LAUNCH", pick_wave_id, request):
            self._enrich_replenishment_settings(pick_wave_id, request.updated_by)
            self._refresh_replenishment_deficit(pick_wave_id, request.updated_by)
            self._reserve_replenishment_sources(pick_wave_id, request.updated_by)
            self._hold_replenishment_rows_without_pick_face_capacity(pick_wave_id, request.updated_by)
            self._release_next_replenishment_queue(pick_wave_id, request.updated_by, include_minimax=False)
            self._sync_replenishment_warehouse_tasks(pick_wave_id, request.updated_by)
            CasePickService(self.gateway).ensure_wave_case_pick_tasks(pick_wave_id, request.updated_by)
            return
        self.gateway.execute_plsql(
            """
            begin
              RRL_PICK_WAVE_API.launch_wave(
                p_pick_wave_id => :pick_wave_id,
                p_launched_by => :updated_by
              );
            end;
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": request.updated_by},
        )
        self._enrich_replenishment_settings(pick_wave_id, request.updated_by or "API")
        self._refresh_replenishment_deficit(pick_wave_id, request.updated_by or "API")
        self._release_cancelled_replenishment_source_reservations(pick_wave_id, request.updated_by or "API")
        self._reserve_replenishment_sources(pick_wave_id, request.updated_by or "API")
        self._hold_replenishment_rows_without_pick_face_capacity(pick_wave_id, request.updated_by or "API")
        self._release_next_replenishment_queue(pick_wave_id, request.updated_by or "API", include_minimax=False)
        self._hold_replenishment_rows_without_pick_face_capacity(pick_wave_id, request.updated_by or "API")
        self._sync_replenishment_warehouse_tasks(pick_wave_id, request.updated_by or "API")
        CasePickService(self.gateway).ensure_wave_case_pick_tasks(pick_wave_id, request.updated_by or "API")

    def release_minimax_replenishment(self, pick_wave_id: int, request: PickWaveActionRequest) -> int:
        updated_by = request.updated_by or "API"
        self._refresh_replenishment_deficit(pick_wave_id, updated_by)
        self._release_cancelled_replenishment_source_reservations(pick_wave_id, updated_by)
        self._reserve_replenishment_sources(pick_wave_id, updated_by)
        self._hold_replenishment_rows_without_pick_face_capacity(pick_wave_id, updated_by)
        released_count = self._release_next_replenishment_queue(pick_wave_id, updated_by)
        self._hold_replenishment_rows_without_pick_face_capacity(pick_wave_id, updated_by)
        self._sync_replenishment_warehouse_tasks(pick_wave_id, updated_by)
        return released_count

    def complete_wave_pick_task(
        self,
        pick_wave_id: int,
        pick_task_id: int,
        request: PickTaskCompleteRequest,
    ) -> dict[str, str | int | float]:
        actor = request.completed_by or "API"
        from ..modules.inventory.public import require_active_stock_release
        require_active_stock_release(self.gateway,request.operation_id)
        types = self.gateway.fetch_all(
            "select t.TASK_TYPE,l.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID "
            "from RRL_PICK_TASK t left join RRL_CASE_PICK_LINE l on l.PICK_TASK_ID=t.PICK_TASK_ID "
            "where t.PICK_TASK_ID=:id", {"id": pick_task_id})
        if types and types[0]["task_type"] == "CASE_PICK":
            raise HTTPException(409, detail={"code": "CASE_PICK_CONFIRM_REQUIRED",
                "case_pick_task_id": types[0].get("case_pick_task_id"),
                "case_pick_line_id": types[0].get("case_pick_line_id"),
                "message": "Confirm the existing CASE line in case-pick-tsd.html; physical stock stays reserved until shipment"})
        if not types or types[0]["task_type"] != "FULL_PALLET":
            raise HTTPException(409, detail={"code": "PHYSICAL_WAVE_TASK_REQUIRED"})
        physical_tasks = self.gateway.fetch_all(
            "select x.TASK_ID from RRL_WAREHOUSE_TASK x "
            "join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=x.SOURCE_TASK_ID "
            "where wt.PICK_WAVE_ID=:wave and wt.PICK_TASK_ID=:pick "
            "and x.TASK_SOURCE='WAVE' and x.SOURCE_DOC_TYPE='PICK_WAVE' "
            "and x.SOURCE_DOC_ID=:wave and x.TASK_TYPE='PICKING_MOVE' "
            "and x.STATUS<>'CANCELLED' fetch first 2 rows only",
            {"wave": pick_wave_id, "pick": pick_task_id})
        if len(physical_tasks) != 1:
            raise HTTPException(409, detail={"code": "WAVE_STAGING_TASK_REQUIRED",
                "message": "Release the existing full-pallet staging task before physical confirmation"})
        from ..modules.inventory.public import complete_existing_warehouse_task as complete_existing_task
        from ..schemas import WarehouseTaskStatusRequest
        task_id = physical_tasks[0]["task_id"]
        result = complete_existing_task(self.gateway, task_id, WarehouseTaskStatusRequest(
            fact_qty=request.fact_qty, scanned_pallet=request.scanned_pallet,
            scanned_from_cell=request.scanned_from_cell, scanned_to_cell=request.scanned_to_cell,
            operation_id=request.operation_id), actor)
        return {**result, "pick_wave_id": pick_wave_id, "pick_task_id": pick_task_id,
                "released_minimax_count": 0}

    def release_wave_staging(self, pick_wave_id: int, request: PickWaveStagingReleaseRequest) -> int:
        from ..modules.inventory.public import release_existing_wave_staging
        return release_existing_wave_staging(self.gateway, pick_wave_id, request)

    def _validate_pick_task_scans(self, task: dict[str, Any], request: PickTaskCompleteRequest) -> None:
        if request.scanned_pallet:
            expected = {str(value).upper() for value in (task.get("pallet_uid"), task.get("sscc")) if value}
            if expected and request.scanned_pallet.upper() not in expected:
                raise HTTPException(status_code=409, detail="Scanned pallet does not match pick task pallet.")
        if request.scanned_from_cell and task.get("source_cell_code"):
            if request.scanned_from_cell.upper() != str(task["source_cell_code"]).upper():
                raise HTTPException(status_code=409, detail="Scanned source cell does not match pick task.")
        if request.scanned_to_cell and task.get("target_cell_code"):
            if request.scanned_to_cell.upper() != str(task["target_cell_code"]).upper():
                raise HTTPException(status_code=409, detail="Scanned target cell does not match pick task.")

    def _apply_case_pick_stock_fact(self, task: dict[str, Any], fact_qty: float) -> None:
        raise HTTPException(409, detail={"code": "CASE_PICK_CONFIRM_REQUIRED"})

    def _enrich_replenishment_settings(self, pick_wave_id: int, updated_by: str) -> None:
        self.gateway.execute(
            """
            update RRL_PICK_WAVE_REPLENISH_TASK rt
               set (
                 REPLENISHMENT_METHOD,
                 REPLENISHMENT_RELEASE_POLICY,
                 REPLENISHMENT_QTY_MODE,
                 RELEASE_TRIGGER_QTY,
                 BOXES_PER_LAYER,
                 BOXES_PER_PALLET,
                 BOX_VOLUME_M3,
                 PICK_FACE_MAX_VOLUME,
                 SAFETY_LAYER_QTY,
                 PREDICTIVE_BUFFER_MIN,
                 PICK_RATE_SOURCE,
                 RECHECK_ON_PICK_EVENT,
                 QTY,
                 STATUS,
                 WAIT_REASON,
                 UPDATED_AT,
                 UPDATED_BY
               ) = (
                 select cfg.REPLENISHMENT_METHOD,
                        cfg.REPLENISHMENT_RELEASE_POLICY,
                        cfg.REPLENISHMENT_QTY_MODE,
                        cfg.RELEASE_TRIGGER_QTY,
                        cfg.BOXES_PER_LAYER,
                        cfg.BOXES_PER_PALLET,
                        cfg.BOX_VOLUME_M3,
                        cfg.PICK_FACE_MAX_VOLUME,
                        cfg.SAFETY_LAYER_QTY,
                        cfg.PREDICTIVE_BUFFER_MIN,
                        cfg.PICK_RATE_SOURCE,
                        cfg.RECHECK_ON_PICK_EVENT,
                        cfg.REPLENISH_QTY,
                        case
                          when rt.STATUS = 'NEW' and cfg.REPLENISHMENT_METHOD = 'MINIMAX' then 'WAIT_MINIMAX'
                          else rt.STATUS
                        end,
                        case
                          when rt.STATUS = 'NEW' and cfg.REPLENISHMENT_METHOD = 'MINIMAX'
                            then 'Waiting until pick-face free stock crosses minimax trigger'
                          else rt.WAIT_REASON
                        end,
                        sysdate,
                        substr(:updated_by, 1, 50)
                   from (
                     select coalesce(
                              case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_METHOD) end,
                              upper(pfa.REPLENISHMENT_METHOD),
                              'IMMEDIATE'
                            ) REPLENISHMENT_METHOD,
                            coalesce(
                              case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_RELEASE_POLICY) end,
                              upper(pfa.REPLENISHMENT_RELEASE_POLICY),
                              'LAYER_TRIGGER'
                            ) REPLENISHMENT_RELEASE_POLICY,
                            coalesce(
                              case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_QTY_MODE) end,
                              upper(pfa.REPLENISHMENT_QTY_MODE),
                              'FILL_TO_VOLUME'
                            ) REPLENISHMENT_QTY_MODE,
                            coalesce(
                              case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.MIN_TRIGGER_BOX_QTY end,
                              pfa.MIN_TRIGGER_BOX_QTY,
                              case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.MIN_TRIGGER_LAYER_QTY * ar.BOXES_PER_LAYER end,
                              pfa.MIN_TRIGGER_LAYER_QTY * pfa.BOXES_PER_LAYER,
                              pf.REPLENISHMENT_TRIGGER_QTY,
                              pfa.MIN_QTY,
                              pf.MIN_CASE_QTY
                            ) RELEASE_TRIGGER_QTY,
                            coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOXES_PER_LAYER end, pfa.BOXES_PER_LAYER) BOXES_PER_LAYER,
                            coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOXES_PER_PALLET end, pfa.BOXES_PER_PALLET) BOXES_PER_PALLET,
                            coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOX_VOLUME_M3 end, pfa.BOX_VOLUME_M3) BOX_VOLUME_M3,
                            pf.MAX_VOLUME PICK_FACE_MAX_VOLUME,
                            coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.SAFETY_LAYER_QTY end, pfa.SAFETY_LAYER_QTY) SAFETY_LAYER_QTY,
                            coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.PREDICTIVE_BUFFER_MIN end, pfa.PREDICTIVE_BUFFER_MIN) PREDICTIVE_BUFFER_MIN,
                            coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.PICK_RATE_SOURCE end, pfa.PICK_RATE_SOURCE, 'MIXED') PICK_RATE_SOURCE,
                            coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.RECHECK_ON_PICK_EVENT end, pfa.RECHECK_ON_PICK_EVENT, 1) RECHECK_ON_PICK_EVENT,
                            greatest(
                              rt.QTY,
                              nvl(
                                case coalesce(
                                       case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_QTY_MODE) end,
                                       upper(pfa.REPLENISHMENT_QTY_MODE),
                                       'FILL_TO_VOLUME'
                                     )
                                  when 'FULL_PALLET' then coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOXES_PER_PALLET end, pfa.BOXES_PER_PALLET)
                                  when 'HALF_PALLET' then ceil(coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOXES_PER_PALLET end, pfa.BOXES_PER_PALLET) / 2)
                                  when 'FILL_TO_VOLUME' then
                                    case
                                      when pf.MAX_VOLUME is not null
                                       and coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOX_VOLUME_M3 end, pfa.BOX_VOLUME_M3) is not null
                                       and coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOX_VOLUME_M3 end, pfa.BOX_VOLUME_M3) > 0
                                        then floor(pf.MAX_VOLUME / coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOX_VOLUME_M3 end, pfa.BOX_VOLUME_M3))
                                      else pfa.MAX_QTY
                                    end
                                end,
                                rt.QTY
                              )
                            ) REPLENISH_QTY
                       from RRL_PICK_TASK t
                       join RRL_PICK_FACE pf
                         on pf.PICK_FACE_ID = t.PICK_FACE_ID
                       left join RRL_PICK_FACE_ARTICUL pfa
                         on pfa.PICK_FACE_ID = pf.PICK_FACE_ID
                        and upper(pfa.ARTICUL) = upper(t.ARTICUL)
                        and pfa.ACTIVE = 1
                        and trunc(sysdate) between trunc(pfa.VALID_FROM) and nvl(trunc(pfa.VALID_TO), date '2999-12-31')
                       left join RRL_ARTICUL_REPLENISH_RULE ar
                         on upper(ar.ARTICUL) = upper(t.ARTICUL)
                        and ar.ACTIVE = 1
                      where t.PICK_TASK_ID = rt.PICK_TASK_ID
                        and rownum = 1
                   ) cfg
                )
             where rt.PICK_WAVE_ID = :pick_wave_id
               and rt.PICK_TASK_ID is not null
               and rt.STATUS in ('NEW', 'RELEASED')
               and exists (
                 select 1
                   from RRL_PICK_TASK t
                  where t.PICK_TASK_ID = rt.PICK_TASK_ID
                    and t.PICK_FACE_ID is not null
               )
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": updated_by},
        )

    def _refresh_replenishment_deficit(self, pick_wave_id: int, updated_by: str) -> None:
        self.gateway.execute(
            """
            merge into RRL_PICK_WAVE_DEMAND d
            using (
              select d.PICK_WAVE_DEMAND_ID,
                     nvl(fs.FREE_QTY, 0) PICK_FACE_FREE_QTY,
                     greatest(nvl(d.DEMAND_QTY, 0) - nvl(fs.FREE_QTY, 0), 0) DEFICIT_QTY,
                     coalesce(
                       case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_METHOD) end,
                       upper(pfa.REPLENISHMENT_METHOD),
                       'IMMEDIATE'
                     ) REPLENISHMENT_METHOD,
                     coalesce(
                       case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_RELEASE_POLICY) end,
                       upper(pfa.REPLENISHMENT_RELEASE_POLICY),
                       'LAYER_TRIGGER'
                     ) REPLENISHMENT_RELEASE_POLICY,
                     coalesce(
                       case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_QTY_MODE) end,
                       upper(pfa.REPLENISHMENT_QTY_MODE),
                       'FILL_TO_VOLUME'
                     ) REPLENISHMENT_QTY_MODE,
                     shelf.MIN_SHELF_LIFE_DAYS,
                     shelf.MIN_SHELF_LIFE_PERCENT,
                     greatest(
                       greatest(nvl(d.DEMAND_QTY, 0) - nvl(fs.FREE_QTY, 0), 0),
                       nvl(
                         case coalesce(
                                case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then upper(ar.REPLENISHMENT_QTY_MODE) end,
                                upper(pfa.REPLENISHMENT_QTY_MODE),
                                'FILL_TO_VOLUME'
                              )
                           when 'FULL_PALLET' then coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOXES_PER_PALLET end, pfa.BOXES_PER_PALLET)
                           when 'HALF_PALLET' then ceil(coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOXES_PER_PALLET end, pfa.BOXES_PER_PALLET) / 2)
                           when 'FILL_TO_VOLUME' then
                             case
                               when pf.MAX_VOLUME is not null
                                and coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOX_VOLUME_M3 end, pfa.BOX_VOLUME_M3) is not null
                                and coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOX_VOLUME_M3 end, pfa.BOX_VOLUME_M3) > 0
                                 then floor(pf.MAX_VOLUME / coalesce(case when nvl(pfa.USE_ARTICUL_REPLENISH_RULE, 0) = 1 then ar.BOX_VOLUME_M3 end, pfa.BOX_VOLUME_M3))
                               else pfa.MAX_QTY
                             end
                         end,
                         greatest(nvl(d.DEMAND_QTY, 0) - nvl(fs.FREE_QTY, 0), 0)
                       )
                     ) REPLENISH_QTY
                from RRL_PICK_WAVE_DEMAND d
                join RRL_PICK_FACE pf
                  on pf.PICK_FACE_ID = d.PICK_FACE_ID
                left join RRL_PICK_FACE_ARTICUL pfa
                  on pfa.PICK_FACE_ID = d.PICK_FACE_ID
                 and upper(pfa.ARTICUL) = upper(d.ARTICUL)
                 and pfa.ACTIVE = 1
                 and trunc(sysdate) between trunc(pfa.VALID_FROM) and nvl(trunc(pfa.VALID_TO), date '2999-12-31')
                left join RRL_ARTICUL_REPLENISH_RULE ar
                  on upper(ar.ARTICUL) = upper(d.ARTICUL)
                 and ar.ACTIVE = 1
                left join (
                  select q.PICK_WAVE_ID,
                         q.ARTICUL,
                         max(q.MIN_SHELF_LIFE_DAYS) MIN_SHELF_LIFE_DAYS,
                         max(q.MIN_SHELF_LIFE_PERCENT) MIN_SHELF_LIFE_PERCENT
                    from (
                      select wo.PICK_WAVE_ID,
                             pl.ARTICUL,
                             nvl((
                               select MIN_SHELF_LIFE_DAYS
                                 from (
                                   select r.MIN_SHELF_LIFE_DAYS
                                     from RRL_CUSTOMER_PRODUCT_RULE r
                                    where r.CUSTOMER_ID = co.CUSTOMER_ID
                                      and r.ACTIVE = 1
                                      and (r.ARTICUL is null or upper(r.ARTICUL) = upper(pl.ARTICUL))
                                      and trunc(sysdate) between trunc(r.VALID_FROM) and nvl(trunc(r.VALID_TO), date '2999-12-31')
                                    order by case when upper(r.ARTICUL) = upper(pl.ARTICUL) then 0 else 1 end,
                                             r.RULE_PRIORITY,
                                             r.CUSTOMER_PRODUCT_RULE_ID
                                 )
                                where rownum = 1
                             ), c.DEFAULT_MIN_SHELF_LIFE_DAYS) MIN_SHELF_LIFE_DAYS,
                             nvl((
                               select MIN_SHELF_LIFE_PERCENT
                                 from (
                                   select r.MIN_SHELF_LIFE_PERCENT
                                     from RRL_CUSTOMER_PRODUCT_RULE r
                                    where r.CUSTOMER_ID = co.CUSTOMER_ID
                                      and r.ACTIVE = 1
                                      and (r.ARTICUL is null or upper(r.ARTICUL) = upper(pl.ARTICUL))
                                      and trunc(sysdate) between trunc(r.VALID_FROM) and nvl(trunc(r.VALID_TO), date '2999-12-31')
                                    order by case when upper(r.ARTICUL) = upper(pl.ARTICUL) then 0 else 1 end,
                                             r.RULE_PRIORITY,
                                             r.CUSTOMER_PRODUCT_RULE_ID
                                 )
                                where rownum = 1
                             ), c.DEFAULT_MIN_SHELF_LIFE_PERCENT) MIN_SHELF_LIFE_PERCENT
                        from RRL_PICK_WAVE_ORDER wo
                        join RRL_PICK_PLAN pp
                          on pp.PICK_PLAN_ID = wo.PICK_PLAN_ID
                        join RRL_PICK_PLAN_LINE pl
                          on pl.PICK_PLAN_ID = pp.PICK_PLAN_ID
                        join RRL_CUSTOMER_ORDER co
                          on co.CUSTOMER_ORDER_ID = pp.CUSTOMER_ORDER_ID
                        left join RRL_CUSTOMER c
                          on c.CUSTOMER_ID = co.CUSTOMER_ID
                       where wo.PICK_WAVE_ID = :pick_wave_id
                         and wo.STATUS = 'ACTIVE'
                    ) q
                   group by q.PICK_WAVE_ID, q.ARTICUL
                ) shelf
                  on shelf.PICK_WAVE_ID = d.PICK_WAVE_ID
                 and shelf.ARTICUL = d.ARTICUL
                outer apply (
                  select sum(greatest(r.REMAIN-r.HARD_RESERVED_BASE,0)) FREE_QTY
                    from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
                    join RRL_CELLS c on c.CELL=r.CELL
                   where r.CELL=d.TARGET_CELL_CODE and p.ARTICUL=d.ARTICUL
                     and r.REMAIN>r.HARD_RESERVED_BASE
                     and c.WARE_ID=(select WARE_ID from RRL_PICK_WAVE where PICK_WAVE_ID=:pick_wave_id)
                     and RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,c.WARE_ID,0,
                       shelf.MIN_SHELF_LIFE_DAYS,shelf.MIN_SHELF_LIFE_PERCENT,'ALLOCATE',null,p.ARTICUL) is null
                ) fs
               where d.PICK_WAVE_ID = :pick_wave_id
                 and d.TASK_TYPE = 'CASE_PICK'
            ) s
            on (d.PICK_WAVE_DEMAND_ID = s.PICK_WAVE_DEMAND_ID)
            when matched then update set
              d.PICK_FACE_FREE_QTY = s.PICK_FACE_FREE_QTY,
              d.REPLENISH_QTY = s.REPLENISH_QTY,
              d.REPLENISHMENT_METHOD = s.REPLENISHMENT_METHOD,
              d.REPLENISHMENT_RELEASE_POLICY = s.REPLENISHMENT_RELEASE_POLICY,
              d.REPLENISHMENT_QTY_MODE = s.REPLENISHMENT_QTY_MODE,
              d.MIN_SHELF_LIFE_DAYS = s.MIN_SHELF_LIFE_DAYS,
              d.MIN_SHELF_LIFE_PERCENT = s.MIN_SHELF_LIFE_PERCENT
            """,
            {"pick_wave_id": pick_wave_id},
        )
        self.gateway.execute(
            """
            merge into RRL_PICK_WAVE_REPLENISH_TASK rt
            using (
              select rt.PICK_WAVE_REPLENISH_TASK_ID,
                     d.PICK_FACE_FREE_QTY,
                     d.REPLENISH_QTY,
                     d.REPLENISHMENT_METHOD,
                     d.REPLENISHMENT_RELEASE_POLICY,
                     d.REPLENISHMENT_QTY_MODE,
                     d.MIN_SHELF_LIFE_DAYS,
                     d.MIN_SHELF_LIFE_PERCENT,
                     row_number() over (
                       partition by rt.PICK_WAVE_ID, rt.ARTICUL, rt.TARGET_CELL_CODE
                       order by rt.PICK_WAVE_REPLENISH_TASK_ID
                     ) RN
                from RRL_PICK_WAVE_REPLENISH_TASK rt
                join RRL_PICK_WAVE_DEMAND d
                  on d.PICK_WAVE_ID = rt.PICK_WAVE_ID
                 and d.ARTICUL = rt.ARTICUL
                 and nvl(d.TARGET_CELL_CODE, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
               where rt.PICK_WAVE_ID = :pick_wave_id
                 and rt.STATUS in ('NEW', 'WAIT_MINIMAX', 'WAIT_FREE_CELL', 'QUEUED', 'RELEASED')
            ) s
            on (rt.PICK_WAVE_REPLENISH_TASK_ID = s.PICK_WAVE_REPLENISH_TASK_ID)
            when matched then update set
              rt.QTY = case when nvl(s.REPLENISH_QTY, 0) > 0 then s.REPLENISH_QTY else rt.QTY end,
              rt.REPLENISHMENT_METHOD = s.REPLENISHMENT_METHOD,
              rt.REPLENISHMENT_RELEASE_POLICY = s.REPLENISHMENT_RELEASE_POLICY,
              rt.REPLENISHMENT_QTY_MODE = s.REPLENISHMENT_QTY_MODE,
              rt.MIN_SHELF_LIFE_DAYS = s.MIN_SHELF_LIFE_DAYS,
              rt.MIN_SHELF_LIFE_PERCENT = s.MIN_SHELF_LIFE_PERCENT,
              rt.STATUS = case
                when nvl(s.REPLENISH_QTY, 0) <= 0 and rt.PICK_TASK_ID is null then 'CANCELLED'
                when s.RN > 1 and rt.STATUS not in ('RELEASED') then 'QUEUED'
                when s.REPLENISHMENT_METHOD = 'MINIMAX' and rt.STATUS not in ('RELEASED', 'QUEUED', 'WAIT_FREE_CELL') then 'WAIT_MINIMAX'
                when s.REPLENISHMENT_METHOD = 'IMMEDIATE' and rt.STATUS = 'NEW' then 'RELEASED'
                else rt.STATUS
              end,
              rt.WAIT_REASON = case
                when nvl(s.REPLENISH_QTY, 0) <= 0 then 'Pick-face stock present; explicit task ownership must be reconciled'
                when s.RN > 1 and rt.STATUS not in ('RELEASED')
                  then 'Queued behind active replenishment for same wave/articul/pick-face'
                when s.REPLENISHMENT_METHOD = 'MINIMAX' and rt.STATUS not in ('RELEASED', 'QUEUED', 'WAIT_FREE_CELL')
                  then 'Waiting until pick-face free stock crosses minimax trigger'
                else null
              end,
              rt.RELEASED_AT = case
                when s.REPLENISHMENT_METHOD = 'IMMEDIATE' and rt.STATUS = 'NEW' and nvl(s.REPLENISH_QTY, 0) > 0 and s.RN = 1
                  then sysdate
                else rt.RELEASED_AT
              end,
              rt.RELEASED_BY = case
                when s.REPLENISHMENT_METHOD = 'IMMEDIATE' and rt.STATUS = 'NEW' and nvl(s.REPLENISH_QTY, 0) > 0 and s.RN = 1
                  then substr(:updated_by, 1, 50)
                else rt.RELEASED_BY
              end,
              rt.UPDATED_AT = sysdate,
              rt.UPDATED_BY = substr(:updated_by, 1, 50)
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": updated_by},
        )

    def _reserve_replenishment_sources(self, pick_wave_id: int, updated_by: str) -> None:
        from ..modules.inventory.public import (require_active_stock_release,
            route_existing_alternative_pick_faces, reserve_existing_wave_sources)
        require_active_stock_release(self.gateway)
        route_existing_alternative_pick_faces(self.gateway, pick_wave_id, updated_by)
        reserve_existing_wave_sources(self.gateway, pick_wave_id, updated_by)

    def _release_cancelled_replenishment_source_reservations(self, pick_wave_id: int, updated_by: str) -> None:
        from ..modules.inventory.public import release_existing_document_reservations
        if release_existing_document_reservations(self.gateway, "PICK_WAVE", pick_wave_id, updated_by,
                "Cancelled replenishment source", only_cancelled=True):
            return
        self.gateway.execute(
            """
            update RRL_STOCK_RESERVATION sr
               set STATUS = 'RELEASED',
                   RELEASED_AT = systimestamp,
                   RELEASED_BY = substr(:updated_by, 1, 100),
                   RELEASE_REASON = 'Replenishment row cancelled before driver task release'
             where sr.RESERVATION_DOMAIN = 'WAVE'
               and sr.SOURCE_DOC_TYPE = 'PICK_WAVE'
               and sr.SOURCE_DOC_ID = :pick_wave_id
               and sr.RESERVATION_KIND = 'HARD'
               and sr.STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
               and exists (
                 select 1
                   from RRL_PICK_WAVE_REPLENISH_TASK rt
                  where rt.PICK_WAVE_REPLENISH_TASK_ID = sr.SOURCE_LINE_ID
                    and rt.PICK_WAVE_ID = :pick_wave_id
                    and rt.STATUS = 'CANCELLED'
                    and not exists (
                      select 1
                        from RRL_WAREHOUSE_TASK wt
                       where wt.TASK_SOURCE = 'WAVE'
                         and wt.TASK_TYPE = 'REPLENISHMENT'
                         and wt.SOURCE_DOC_TYPE = 'PICK_WAVE'
                         and wt.SOURCE_DOC_ID = rt.PICK_WAVE_ID
                         and wt.SOURCE_TASK_ID = rt.PICK_WAVE_REPLENISH_TASK_ID
                    )
               )
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": updated_by},
        )
        self.gateway.execute(
            """
            update RRL_PICK_WAVE_REPLENISH_TASK rt
               set SOURCE_RESERVATION_ID = null,
                   PALLET_UID = null,
                   SOURCE_CELL_CODE = null,
                   SOURCE_AVAILABLE_QTY = null,
                   SOURCE_PRODUCED_DATE = null,
                   SOURCE_EXPIRY_DATE = null,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where rt.PICK_WAVE_ID = :pick_wave_id
               and rt.STATUS = 'CANCELLED'
               and rt.SOURCE_RESERVATION_ID is not null
               and not exists (
                 select 1
                   from RRL_WAREHOUSE_TASK wt
                  where wt.TASK_SOURCE = 'WAVE'
                    and wt.TASK_TYPE = 'REPLENISHMENT'
                    and wt.SOURCE_DOC_TYPE = 'PICK_WAVE'
                    and wt.SOURCE_DOC_ID = rt.PICK_WAVE_ID
                    and wt.SOURCE_TASK_ID = rt.PICK_WAVE_REPLENISH_TASK_ID
               )
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": updated_by},
        )

    def _hold_replenishment_rows_without_pick_face_capacity(self, pick_wave_id: int, updated_by: str) -> None:
        from ..modules.inventory.public import hold_existing_replenishment_capacity
        hold_existing_replenishment_capacity(self.gateway, pick_wave_id, updated_by)

    def _release_next_replenishment_queue(
        self,
        pick_wave_id: int,
        updated_by: str,
        include_minimax: bool = True,
    ) -> int:
        from ..modules.inventory.public import route_existing_alternative_pick_faces
        dynamic_count = route_existing_alternative_pick_faces(self.gateway, pick_wave_id, updated_by)
        minimax_count = 0
        if include_minimax:
            minimax_count = self.gateway.execute(
            """
            update RRL_PICK_WAVE_REPLENISH_TASK rt
               set STATUS = 'RELEASED',
                   RELEASED_AT = sysdate,
                   RELEASED_BY = substr(:updated_by, 1, 50),
                   WAIT_REASON = null,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where rt.PICK_WAVE_ID = :pick_wave_id
               and rt.STATUS in ('WAIT_MINIMAX', 'QUEUED')
               and nvl(rt.REPLENISHMENT_METHOD, 'IMMEDIATE') = 'MINIMAX'
               and rt.SOURCE_RESERVATION_ID is not null
               and rt.PICK_WAVE_REPLENISH_TASK_ID = (
                 select min(q.PICK_WAVE_REPLENISH_TASK_ID)
                   from RRL_PICK_WAVE_REPLENISH_TASK q
                  where q.PICK_WAVE_ID = rt.PICK_WAVE_ID
                    and q.ARTICUL = rt.ARTICUL
                    and nvl(q.TARGET_CELL_CODE, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and q.STATUS in ('WAIT_MINIMAX', 'QUEUED')
                    and q.SOURCE_RESERVATION_ID is not null
               )
               and not exists (
                 select 1
                   from RRL_WAREHOUSE_TASK wt
                  where wt.TASK_SOURCE = 'WAVE'
                    and wt.TASK_TYPE = 'REPLENISHMENT'
                    and wt.SOURCE_DOC_TYPE = 'PICK_WAVE'
                    and wt.SOURCE_DOC_ID = rt.PICK_WAVE_ID
                    and wt.TARGET_ARTICUL = rt.ARTICUL
                    and nvl(wt.TO_CELL, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and wt.STATUS in ('PLANNED', 'ASSIGNED', 'IN_PROGRESS')
               )
               and not exists (
                 select 1
                   from RRL_PICK_WAVE_REPLENISH_TASK active_rt
                  where active_rt.PICK_WAVE_ID = rt.PICK_WAVE_ID
                    and active_rt.PICK_WAVE_REPLENISH_TASK_ID <> rt.PICK_WAVE_REPLENISH_TASK_ID
                    and active_rt.ARTICUL = rt.ARTICUL
                    and nvl(active_rt.TARGET_CELL_CODE, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and active_rt.STATUS in ('RELEASED', 'ASSIGNED', 'IN_PROGRESS')
               )
               and nvl(rt.RELEASE_TRIGGER_QTY, 0) >= (
                 select nvl(d.PICK_FACE_FREE_QTY, 0)
                   from RRL_PICK_WAVE_DEMAND d
                  where d.PICK_WAVE_ID = rt.PICK_WAVE_ID
                    and d.ARTICUL = rt.ARTICUL
                    and nvl(d.TARGET_CELL_CODE, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and rownum = 1
               )
               and nvl((
                 select d.REPLENISH_QTY
                   from RRL_PICK_WAVE_DEMAND d
                  where d.PICK_WAVE_ID = rt.PICK_WAVE_ID
                    and d.ARTICUL = rt.ARTICUL
                    and nvl(d.TARGET_CELL_CODE, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and rownum = 1
               ), 0) > 0
               and (
                 rt.PICK_FACE_MAX_VOLUME is null
                 or rt.BOX_VOLUME_M3 is null
                 or rt.BOX_VOLUME_M3 <= 0
                 or (
                   nvl((
                     select sum(nvl(r.REMAIN, 0))
                       from RRL_REMAINS r
                      where r.CELL = rt.TARGET_CELL_CODE
                   ), 0) + nvl(rt.QTY, 0)
                 ) * rt.BOX_VOLUME_M3 <= rt.PICK_FACE_MAX_VOLUME
               )
            """,
                {"pick_wave_id": pick_wave_id, "updated_by": updated_by},
            )
        immediate_count = self.gateway.execute(
            """
            update RRL_PICK_WAVE_REPLENISH_TASK rt
               set STATUS = 'RELEASED',
                   RELEASED_AT = sysdate,
                   RELEASED_BY = substr(:updated_by, 1, 50),
                   WAIT_REASON = null,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where rt.PICK_WAVE_ID = :pick_wave_id
               and rt.STATUS = 'QUEUED'
               and nvl(rt.REPLENISHMENT_METHOD, 'IMMEDIATE') <> 'MINIMAX'
               and rt.SOURCE_RESERVATION_ID is not null
               and rt.PICK_WAVE_REPLENISH_TASK_ID = (
                 select min(q.PICK_WAVE_REPLENISH_TASK_ID)
                   from RRL_PICK_WAVE_REPLENISH_TASK q
                  where q.PICK_WAVE_ID = rt.PICK_WAVE_ID
                    and q.ARTICUL = rt.ARTICUL
                    and nvl(q.TARGET_CELL_CODE, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and q.STATUS = 'QUEUED'
                    and nvl(q.REPLENISHMENT_METHOD, 'IMMEDIATE') <> 'MINIMAX'
                    and q.SOURCE_RESERVATION_ID is not null
               )
               and not exists (
                 select 1
                   from RRL_WAREHOUSE_TASK wt
                  where wt.TASK_SOURCE = 'WAVE'
                    and wt.TASK_TYPE = 'REPLENISHMENT'
                    and wt.SOURCE_DOC_TYPE = 'PICK_WAVE'
                    and wt.SOURCE_DOC_ID = rt.PICK_WAVE_ID
                    and wt.TARGET_ARTICUL = rt.ARTICUL
                    and nvl(wt.TO_CELL, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and wt.STATUS in ('PLANNED', 'ASSIGNED', 'IN_PROGRESS')
               )
               and not exists (
                 select 1
                   from RRL_PICK_WAVE_REPLENISH_TASK active_rt
                  where active_rt.PICK_WAVE_ID = rt.PICK_WAVE_ID
                    and active_rt.PICK_WAVE_REPLENISH_TASK_ID <> rt.PICK_WAVE_REPLENISH_TASK_ID
                    and active_rt.ARTICUL = rt.ARTICUL
                    and nvl(active_rt.TARGET_CELL_CODE, chr(0)) = nvl(rt.TARGET_CELL_CODE, chr(0))
                    and active_rt.STATUS in ('RELEASED', 'ASSIGNED', 'IN_PROGRESS')
               )
               and (
                 rt.PICK_FACE_MAX_VOLUME is null
                 or rt.BOX_VOLUME_M3 is null
                 or rt.BOX_VOLUME_M3 <= 0
                 or (
                   nvl((
                     select sum(nvl(r.REMAIN, 0))
                       from RRL_REMAINS r
                      where r.CELL = rt.TARGET_CELL_CODE
                   ), 0) + nvl(rt.QTY, 0)
                 ) * rt.BOX_VOLUME_M3 <= rt.PICK_FACE_MAX_VOLUME
               )
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": updated_by},
        )
        dynamic_released = dynamic_count if isinstance(dynamic_count, int) and dynamic_count > 0 else 0
        return dynamic_released + minimax_count + immediate_count

    def cancel_wave(self, pick_wave_id: int, request: PickWaveActionRequest) -> None:
        if self._post_wave_command("WAVE_CANCEL", pick_wave_id, request):
            return
        self.gateway.execute_plsql(
            """
            begin
              RRL_PICK_WAVE_API.cancel_wave(
                p_pick_wave_id => :pick_wave_id,
                p_reason => :reason,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"pick_wave_id": pick_wave_id, **request.model_dump(exclude={"operation_id"})},
        )
        self._cancel_replenishment_warehouse_tasks(pick_wave_id, request.updated_by or "API", request.reason)

    def release_wave_reservations(self, pick_wave_id: int, request: PickWaveActionRequest) -> None:
        if self._post_wave_command("WAVE_RELEASE", pick_wave_id, request):
            return
        self.gateway.execute_plsql(
            """
            begin
              RRL_PICK_WAVE_API.release_reservations(
                p_pick_wave_id => :pick_wave_id,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"pick_wave_id": pick_wave_id, "updated_by": request.updated_by},
        )
        self._cancel_replenishment_warehouse_tasks(
            pick_wave_id,
            request.updated_by or "API",
            "Wave reservations released.",
        )

    def _sync_replenishment_warehouse_tasks(self, pick_wave_id: int, created_by: str) -> None:
        from ..modules.resources.public import sync_existing_wave_tasks
        sync_existing_wave_tasks(self.gateway, pick_wave_id, created_by)

    def _cancel_replenishment_warehouse_tasks(
        self,
        pick_wave_id: int,
        cancelled_by: str,
        reason: str | None,
    ) -> None:
        from ..modules.inventory.public import release_existing_document_reservations
        if not release_existing_document_reservations(self.gateway, "PICK_WAVE", pick_wave_id, cancelled_by,
                reason or "Wave reservations released"):
            self.gateway.execute(
                """
                update RRL_STOCK_RESERVATION
                   set STATUS = 'RELEASED',
                       RELEASED_AT = systimestamp,
                       RELEASED_BY = substr(:cancelled_by, 1, 100),
                       RELEASE_REASON = :reason
                 where RESERVATION_DOMAIN = 'WAVE'
                   and SOURCE_DOC_TYPE = 'PICK_WAVE'
                   and SOURCE_DOC_ID = :pick_wave_id
                   and STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
                """,
                {
                    "pick_wave_id": pick_wave_id,
                    "cancelled_by": cancelled_by,
                    "reason": reason,
                },
            )
        self.gateway.execute(
            """
            update RRL_PICK_FACE_ASSIGNMENT
               set STATUS = 'RELEASED',
                   RELEASED_AT = sysdate,
                   RELEASED_BY = substr(:cancelled_by, 1, 50),
                   RELEASE_REASON = :reason
             where PICK_WAVE_ID = :pick_wave_id
               and STATUS = 'ACTIVE'
            """,
            {
                "pick_wave_id": pick_wave_id,
                "cancelled_by": cancelled_by,
                "reason": reason,
            },
        )
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK
               set STATUS = 'CANCELLED',
                   CANCELLED_AT = systimestamp,
                   CANCELLED_BY = :cancelled_by,
                   LAST_ERROR = :reason
             where TASK_SOURCE = 'WAVE'
               and TASK_TYPE = 'REPLENISHMENT'
               and SOURCE_DOC_TYPE = 'PICK_WAVE'
               and SOURCE_DOC_ID = :pick_wave_id
               and STATUS in ('PLANNED', 'ASSIGNED')
            """,
            {
                "pick_wave_id": pick_wave_id,
                "cancelled_by": cancelled_by,
                "reason": reason,
            },
        )

    def list_waves(
        self,
        status: str | None = None,
        ware_id: int | None = None,
        customer_id: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if status:
            conditions.append("upper(w.STATUS) = :status")
            params["status"] = status.upper()
        if ware_id is not None:
            conditions.append("w.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if customer_id is not None:
            conditions.append(
                "exists (select 1 from RRL_PICK_WAVE_ORDER wo "
                "where wo.PICK_WAVE_ID = w.PICK_WAVE_ID "
                "and wo.STATUS = 'ACTIVE' and wo.CUSTOMER_ID = :customer_id)"
            )
            params["customer_id"] = customer_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select w.PICK_WAVE_ID,
                       w.WAVE_CODE,
                       w.WAVE_NAME,
                       w.WARE_ID,
                       wa.NAME WARE_NAME,
                       w.ROUTE_ID,
                       r.ROUTE_CODE,
                       w.DOCK_ID,
                       w.STATUS,
                       w.WAVE_KIND,
                       w.PLANNED_START_AT,
                       w.PLANNED_FINISH_AT,
                       w.MAX_CUSTOMERS,
                       w.CUSTOMER_COUNT,
                       w.ORDER_COUNT,
                       w.PLAN_COUNT,
                       w.TASK_COUNT,
                       w.HARD_RESERVE_QTY,
                       w.CREATED_AT,
                       w.CREATED_BY,
                       w.LAUNCHED_AT,
                       w.LAUNCHED_BY,
                       w.CANCELLED_AT,
                       w.CANCELLED_BY,
                       w.UPDATED_AT,
                       w.UPDATED_BY
                  from RRL_PICK_WAVE w
                  left join RRL_WARES wa
                    on wa.ID = w.WARE_ID
                  left join RRL_PICK_ROUTE r
                    on r.PICK_ROUTE_ID = w.ROUTE_ID
                  {where_sql}
                 order by w.PICK_WAVE_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_wave_candidates(
        self,
        ware_id: int | None = None,
        route_id: int | None = None,
        dock_id: int | None = None,
        shipment_from: str | None = None,
        shipment_to: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = [
            "p.STATUS in ('PLANNED_FULL', 'PLANNED_PARTIAL')",
            "not exists ("
            "select 1 from RRL_PICK_WAVE_ORDER wo "
            "join RRL_PICK_WAVE w on w.PICK_WAVE_ID = wo.PICK_WAVE_ID "
            "where wo.PICK_PLAN_ID = p.PICK_PLAN_ID "
            "and wo.STATUS = 'ACTIVE' "
            "and w.STATUS in ('DRAFT', 'PREVIEW', 'LAUNCHED'))",
        ]
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if ware_id is not None:
            conditions.append("p.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if route_id is not None:
            conditions.append("p.ROUTE_ID = :route_id")
            params["route_id"] = route_id
        if dock_id is not None:
            conditions.append("p.DOCK_ID = :dock_id")
            params["dock_id"] = dock_id
        if shipment_from:
            conditions.append("co.SHIPMENT_DATE >= to_date(:shipment_from, 'YYYY-MM-DD')")
            params["shipment_from"] = shipment_from
        if shipment_to:
            conditions.append("co.SHIPMENT_DATE < to_date(:shipment_to, 'YYYY-MM-DD') + 1")
            params["shipment_to"] = shipment_to
        where_sql = " where " + " and ".join(conditions)
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select p.PICK_PLAN_ID,
                       p.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       co.SHIPMENT_DATE,
                       p.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       p.WARE_ID,
                       wa.NAME WARE_NAME,
                       p.ROUTE_ID,
                       p.DOCK_ID,
                       p.STATUS,
                       p.PLAN_STRATEGY,
                       p.TOTAL_ORDER_QTY,
                       p.TOTAL_PLANNED_QTY,
                       p.TOTAL_SHORTAGE_QTY,
                       count(distinct t.PICK_TASK_ID) TASK_COUNT,
                       count(distinct pr.PICK_RESERVATION_ID) RESERVATION_COUNT,
                       p.CREATED_AT,
                       p.CREATED_BY
                  from RRL_PICK_PLAN p
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = p.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = p.CUSTOMER_ID
                  left join RRL_WARES wa
                    on wa.ID = p.WARE_ID
                  left join RRL_PICK_TASK t
                    on t.PICK_PLAN_ID = p.PICK_PLAN_ID
                  left join RRL_PICK_RESERVATION pr
                    on pr.PICK_PLAN_ID = p.PICK_PLAN_ID
                   and pr.RESERVATION_STATUS = 'ACTIVE'
                  {where_sql}
                 group by p.PICK_PLAN_ID,
                          p.CUSTOMER_ORDER_ID,
                          co.ORDER_NO,
                          co.SHIPMENT_DATE,
                          p.CUSTOMER_ID,
                          c.CUSTOMER_NAME,
                          p.WARE_ID,
                          wa.NAME,
                          p.ROUTE_ID,
                          p.DOCK_ID,
                          p.STATUS,
                          p.PLAN_STRATEGY,
                          p.TOTAL_ORDER_QTY,
                          p.TOTAL_PLANNED_QTY,
                          p.TOTAL_SHORTAGE_QTY,
                          p.CREATED_AT,
                          p.CREATED_BY
                 order by co.SHIPMENT_DATE nulls last, p.PICK_PLAN_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_wave_header(self, pick_wave_id: int) -> dict[str, Any] | None:
        from ..modules.inventory.public import existing_wave_header
        return existing_wave_header(self.gateway,pick_wave_id)

    def get_wave(self, pick_wave_id: int) -> dict[str, Any] | None:
        wave = self.get_wave_header(pick_wave_id)
        if wave is None:
            return None
        wave["orders"] = self.gateway.fetch_all(
            """
            select wo.PICK_WAVE_ORDER_ID,
                   wo.PICK_PLAN_ID,
                   wo.CUSTOMER_ORDER_ID,
                   wo.ORDER_NO,
                   wo.CUSTOMER_ID,
                   c.CUSTOMER_NAME,
                   wo.STATUS,
                   wo.CREATED_AT,
                   wo.CREATED_BY
              from RRL_PICK_WAVE_ORDER wo
              left join RRL_CUSTOMER c
                on c.CUSTOMER_ID = wo.CUSTOMER_ID
             where wo.PICK_WAVE_ID = :pick_wave_id
             order by wo.PICK_WAVE_ORDER_ID
            """,
            {"pick_wave_id": pick_wave_id},
        )
        wave["lines"] = self.list_wave_lines(pick_wave_id)
        wave["demand"] = self.list_wave_demand(pick_wave_id)
        wave["reservations"] = self.list_wave_reservations(pick_wave_id, limit=500)
        wave["replenishment_tasks"] = self.list_wave_replenishment_tasks(pick_wave_id, limit=500)
        wave["tasks"] = self.list_wave_tasks(pick_wave_id, limit=500)
        wave["shortages"] = self.list_wave_shortages(pick_wave_id, limit=500)
        return wave
    def get_wave_readiness(self, pick_wave_id: int) -> dict[str, Any] | None:
        waves = self.gateway.fetch_all(
            """
            select PICK_WAVE_ID,
                   WAVE_CODE,
                   WAVE_NAME,
                   STATUS
              from RRL_PICK_WAVE
             where PICK_WAVE_ID = :pick_wave_id
            """,
            {"pick_wave_id": pick_wave_id},
        )
        if not waves:
            return None

        blockers: list[dict[str, Any]] = []
        replenishment = self.gateway.fetch_all(
            """
            select STATUS,
                   count(*) CNT
              from RRL_PICK_WAVE_REPLENISH_TASK
             where PICK_WAVE_ID = :pick_wave_id
               and STATUS not in ('DONE', 'CANCELLED')
             group by STATUS
             order by STATUS
            """,
            {"pick_wave_id": pick_wave_id},
        )
        for row in replenishment:
            blockers.append(
                {
                    "blocker_type": "REPLENISHMENT",
                    "severity": "BLOCKER",
                    "status": row["status"],
                    "count": int(row["cnt"] or 0),
                    "message": "Open pick-face replenishment task.",
                }
            )

        staging = self.gateway.fetch_all(
            """
            select STATUS,
                   count(*) CNT
              from (
                select case
                         when wt.STATUS <> 'DONE' then wt.STATUS
                         when wh.TASK_ID is null then 'WAREHOUSE_TASK_MISSING'
                         else wh.STATUS
                       end STATUS
                  from RRL_PICK_WAVE_TASK wt
                  left join RRL_WAREHOUSE_TASK wh
                    on wh.TASK_SOURCE = 'WAVE'
                   and wh.TASK_TYPE = 'PICKING_MOVE'
                   and wh.SOURCE_DOC_TYPE = 'PICK_WAVE'
                   and wh.SOURCE_TASK_ID = wt.PICK_WAVE_TASK_ID
                 where wt.PICK_WAVE_ID = :pick_wave_id
                   and wt.TASK_TYPE = 'FULL_PALLET'
                   and (
                        wt.STATUS <> 'DONE'
                     or wh.TASK_ID is null
                     or wh.STATUS <> 'DONE'
                   )
              )
             group by STATUS
             order by STATUS
            """,
            {"pick_wave_id": pick_wave_id},
        )
        for row in staging:
            blockers.append(
                {
                    "blocker_type": "STAGING",
                    "severity": "BLOCKER",
                    "status": row["status"],
                    "count": int(row["cnt"] or 0),
                    "message": "Open full-pallet staging task.",
                }
            )

        case_pick = self.gateway.fetch_all(
            """
            select STATUS,
                   count(*) CNT
              from RRL_PICK_WAVE_TASK
             where PICK_WAVE_ID = :pick_wave_id
               and TASK_TYPE = 'CASE_PICK'
               and STATUS not in ('DONE', 'CANCELLED')
             group by STATUS
             order by STATUS
            """,
            {"pick_wave_id": pick_wave_id},
        )
        for row in case_pick:
            blockers.append(
                {
                    "blocker_type": "CASE_PICK",
                    "severity": "BLOCKER",
                    "status": row["status"],
                    "count": int(row["cnt"] or 0),
                    "message": "Open case-picking task.",
                }
            )

        sync_errors = self.gateway.fetch_all(
            """
            select SYNC_STATUS,
                   count(*) CNT
              from RRL_WAREHOUSE_TASK_SYNC
             where TASK_SOURCE = 'WAVE'
               and SOURCE_DOC_TYPE = 'PICK_WAVE'
               and SOURCE_DOC_ID = :pick_wave_id
               and SYNC_STATUS <> 'SYNCED'
             group by SYNC_STATUS
             order by SYNC_STATUS
            """,
            {"pick_wave_id": pick_wave_id},
        )
        for row in sync_errors:
            blockers.append(
                {
                    "blocker_type": "DOMAIN_SYNC",
                    "severity": "BLOCKER",
                    "status": row["sync_status"],
                    "count": int(row["cnt"] or 0),
                    "message": "Warehouse-task fact is not synchronized to the wave domain.",
                }
            )

        shortages = self.gateway.fetch_all(
            """
            select REASON_CODE,
                   count(*) CNT,
                   sum(SHORTAGE_QTY) SHORTAGE_QTY
              from RRL_PICK_WAVE_SHORTAGE
             where PICK_WAVE_ID = :pick_wave_id
               and SHORTAGE_QTY > 0
             group by REASON_CODE
             order by REASON_CODE
            """,
            {"pick_wave_id": pick_wave_id},
        )
        for row in shortages:
            blockers.append(
                {
                    "blocker_type": "SHORTAGE",
                    "severity": "BLOCKER",
                    "status": row["reason_code"],
                    "count": int(row["cnt"] or 0),
                    "qty": float(row["shortage_qty"] or 0),
                    "message": "Wave has unresolved shortage.",
                }
            )

        summary = {
            "open_replenishment_count": sum(
                int(row["cnt"] or 0) for row in replenishment
            ),
            "open_staging_count": sum(int(row["cnt"] or 0) for row in staging),
            "open_case_pick_count": sum(int(row["cnt"] or 0) for row in case_pick),
            "sync_error_count": sum(int(row["cnt"] or 0) for row in sync_errors),
            "shortage_count": sum(int(row["cnt"] or 0) for row in shortages),
            "shortage_qty": sum(float(row["shortage_qty"] or 0) for row in shortages),
        }
        return {
            "pick_wave_id": pick_wave_id,
            "wave_code": waves[0]["wave_code"],
            "wave_name": waves[0]["wave_name"],
            "wave_status": waves[0]["status"],
            "is_ready": not blockers,
            "status": "READY" if not blockers else "BLOCKED",
            "summary": summary,
            "blockers": blockers,
        }

    def list_wave_lines(self, pick_wave_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select wl.PICK_WAVE_LINE_ID,
                   wl.PICK_WAVE_ORDER_ID,
                   wl.PICK_PLAN_ID,
                   wl.PICK_PLAN_LINE_ID,
                   wl.CUSTOMER_ORDER_ROW_ID,
                   wl.ARTICUL,
                   wl.REQUESTED_QTY,
                   wl.PLANNED_QTY,
                   wl.SHORTAGE_QTY,
                   wl.STATUS,
                   wl.CREATED_AT,
                   wl.CREATED_BY
              from RRL_PICK_WAVE_LINE wl
             where wl.PICK_WAVE_ID = :pick_wave_id
             order by wl.PICK_WAVE_LINE_ID
            """,
            {"pick_wave_id": pick_wave_id},
        )

    def list_wave_demand(self, pick_wave_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select PICK_WAVE_DEMAND_ID,
                   ARTICUL,
                   TASK_TYPE,
                   TARGET_CELL_CODE,
                   PICK_FACE_ID,
                   PICK_ROUTE_CELL_ID,
                   DEMAND_QTY,
                   TASK_COUNT,
                   CREATED_AT,
                   CREATED_BY
              from RRL_PICK_WAVE_DEMAND
             where PICK_WAVE_ID = :pick_wave_id
             order by TASK_TYPE, TARGET_CELL_CODE, ARTICUL
            """,
            {"pick_wave_id": pick_wave_id},
        )

    def list_wave_reservations(self, pick_wave_id: int, limit: int = 200) -> list[dict[str, Any]]:
        params = {"pick_wave_id": pick_wave_id, "limit": min(max(limit, 1), 1000)}
        return self.gateway.fetch_all(
            """
            select *
              from (
                select wr.PICK_WAVE_RESERVATION_ID,
                       wr.PICK_RESERVATION_ID,
                       wr.PICK_TASK_ID,
                       wr.PICK_PLAN_ID,
                       wr.PICK_PLAN_LINE_ID,
                       wr.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       wr.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       wr.RESERVATION_STATUS,
                       wr.PALLET_UID,
                       wr.SSCC,
                       wr.ARTICUL,
                       wr.SOURCE_CELL_CODE,
                       wr.RESERVED_QTY,
                       wr.CREATED_AT,
                       wr.CREATED_BY,
                       wr.RELEASED_AT,
                       wr.UPDATED_AT,
                       wr.UPDATED_BY
                  from RRL_PICK_WAVE_RESERVATION wr
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = wr.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = wr.CUSTOMER_ID
                 where wr.PICK_WAVE_ID = :pick_wave_id
                 order by wr.PICK_WAVE_RESERVATION_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_wave_replenishment_tasks(self, pick_wave_id: int, limit: int = 200) -> list[dict[str, Any]]:
        params = {"pick_wave_id": pick_wave_id, "limit": min(max(limit, 1), 1000)}
        return self.gateway.fetch_all(
            """
            select *
              from (
                select PICK_WAVE_REPLENISH_TASK_ID,
                       PICK_TASK_ID,
                       STATUS,
                       ARTICUL,
                       PALLET_UID,
                       SOURCE_CELL_CODE,
                       TARGET_CELL_CODE,
                       QTY,
                       REPLENISHMENT_METHOD,
                       REPLENISHMENT_RELEASE_POLICY,
                       REPLENISHMENT_QTY_MODE,
                       RELEASE_TRIGGER_QTY,
                       BOXES_PER_LAYER,
                       BOXES_PER_PALLET,
                       BOX_VOLUME_M3,
                       PICK_FACE_MAX_VOLUME,
                       SAFETY_LAYER_QTY,
                       PREDICTIVE_BUFFER_MIN,
                       PICK_RATE_SOURCE,
                       RECHECK_ON_PICK_EVENT,
                       WAIT_REASON,
                       RELEASED_AT,
                       RELEASED_BY,
                       SOURCE_RESERVATION_ID,
                       SOURCE_AVAILABLE_QTY,
                       SOURCE_PRODUCED_DATE,
                       SOURCE_EXPIRY_DATE,
                       MIN_SHELF_LIFE_DAYS,
                       MIN_SHELF_LIFE_PERCENT,
                       PICK_SEQUENCE,
                       CREATED_AT,
                       CREATED_BY,
                       UPDATED_AT,
                       UPDATED_BY,
                       WAREHOUSE_TASK_ID,
                       WAREHOUSE_TASK_STATUS,
                       WAREHOUSE_ASSIGNED_TO,
                       WAREHOUSE_FINISHED_AT
                  from (
                    select rt.PICK_WAVE_REPLENISH_TASK_ID,
                           rt.PICK_TASK_ID,
                           rt.STATUS,
                           rt.ARTICUL,
                           rt.PALLET_UID,
                           rt.SOURCE_CELL_CODE,
                           rt.TARGET_CELL_CODE,
                           rt.QTY,
                           rt.REPLENISHMENT_METHOD,
                           rt.REPLENISHMENT_RELEASE_POLICY,
                           rt.REPLENISHMENT_QTY_MODE,
                           rt.RELEASE_TRIGGER_QTY,
                           rt.BOXES_PER_LAYER,
                           rt.BOXES_PER_PALLET,
                           rt.BOX_VOLUME_M3,
                           rt.PICK_FACE_MAX_VOLUME,
                           rt.SAFETY_LAYER_QTY,
                           rt.PREDICTIVE_BUFFER_MIN,
                           rt.PICK_RATE_SOURCE,
                           rt.RECHECK_ON_PICK_EVENT,
                           rt.WAIT_REASON,
                           rt.RELEASED_AT,
                           rt.RELEASED_BY,
                           rt.SOURCE_RESERVATION_ID,
                           rt.SOURCE_AVAILABLE_QTY,
                           rt.SOURCE_PRODUCED_DATE,
                           rt.SOURCE_EXPIRY_DATE,
                           rt.MIN_SHELF_LIFE_DAYS,
                           rt.MIN_SHELF_LIFE_PERCENT,
                           rt.PICK_SEQUENCE,
                           rt.CREATED_AT,
                           rt.CREATED_BY,
                           rt.UPDATED_AT,
                           rt.UPDATED_BY,
                           wt.TASK_ID WAREHOUSE_TASK_ID,
                           wt.STATUS WAREHOUSE_TASK_STATUS,
                           wt.ASSIGNED_TO WAREHOUSE_ASSIGNED_TO,
                           wt.FINISHED_AT WAREHOUSE_FINISHED_AT
                      from RRL_PICK_WAVE_REPLENISH_TASK rt
                      left join RRL_WAREHOUSE_TASK wt
                        on wt.TASK_SOURCE = 'WAVE'
                       and wt.TASK_TYPE = 'REPLENISHMENT'
                       and wt.SOURCE_TASK_ID = rt.PICK_WAVE_REPLENISH_TASK_ID
                     where rt.PICK_WAVE_ID = :pick_wave_id
                  )
                 order by PICK_SEQUENCE nulls last, PICK_WAVE_REPLENISH_TASK_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_wave_tasks(self, pick_wave_id: int, limit: int = 200) -> list[dict[str, Any]]:
        params = {"pick_wave_id": pick_wave_id, "limit": min(max(limit, 1), 1000)}
        return self.gateway.fetch_all(
            """
            select *
              from (
                select PICK_WAVE_TASK_ID,
                       PICK_TASK_ID,
                       PICK_WAVE_REPLENISH_TASK_ID,
                       TASK_TYPE,
                       STATUS,
                       ARTICUL,
                       PALLET_UID,
                       SOURCE_CELL_CODE,
                       TARGET_CELL_CODE,
                       QTY,
                       FACT_QTY,
                       PICK_SEQUENCE,
                       PICK_FACE_ID,
                       PICK_ROUTE_CELL_ID,
                       DONE_AT,
                       DONE_BY,
                       CREATED_AT,
                       CREATED_BY,
                       UPDATED_AT,
                       UPDATED_BY,
                       WAREHOUSE_TASK_ID,
                       WAREHOUSE_TASK_STATUS,
                       WAREHOUSE_ASSIGNED_TO,
                       WAREHOUSE_FINISHED_AT
                  from (
                    select wt.PICK_WAVE_TASK_ID,
                           wt.PICK_TASK_ID,
                           wt.PICK_WAVE_REPLENISH_TASK_ID,
                           wt.TASK_TYPE,
                           wt.STATUS,
                           wt.ARTICUL,
                           wt.PALLET_UID,
                           wt.SOURCE_CELL_CODE,
                           wt.TARGET_CELL_CODE,
                           wt.QTY,
                           wt.FACT_QTY,
                           wt.PICK_SEQUENCE,
                           wt.PICK_FACE_ID,
                           wt.PICK_ROUTE_CELL_ID,
                           wt.DONE_AT,
                           wt.DONE_BY,
                           wt.CREATED_AT,
                           wt.CREATED_BY,
                           wt.UPDATED_AT,
                           wt.UPDATED_BY,
                           wh.TASK_ID WAREHOUSE_TASK_ID,
                           wh.STATUS WAREHOUSE_TASK_STATUS,
                           wh.ASSIGNED_TO WAREHOUSE_ASSIGNED_TO,
                           wh.FINISHED_AT WAREHOUSE_FINISHED_AT
                      from RRL_PICK_WAVE_TASK wt
                      left join RRL_WAREHOUSE_TASK wh
                        on wh.TASK_SOURCE = 'WAVE'
                       and wh.TASK_TYPE = 'PICKING_MOVE'
                       and wh.SOURCE_DOC_TYPE = 'PICK_WAVE'
                       and wh.SOURCE_TASK_ID = wt.PICK_WAVE_TASK_ID
                     where wt.PICK_WAVE_ID = :pick_wave_id
                  )
                 order by PICK_SEQUENCE nulls last, PICK_WAVE_TASK_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_wave_shortages(self, pick_wave_id: int, limit: int = 200) -> list[dict[str, Any]]:
        params = {"pick_wave_id": pick_wave_id, "limit": min(max(limit, 1), 1000)}
        return self.gateway.fetch_all(
            """
            select *
              from (
                select PICK_WAVE_SHORTAGE_ID,
                       PICK_SHORTAGE_ID,
                       PICK_PLAN_ID,
                       CUSTOMER_ORDER_ID,
                       CUSTOMER_ID,
                       ARTICUL,
                       REQUESTED_QTY,
                       PLANNED_QTY,
                       SHORTAGE_QTY,
                       REASON_CODE,
                       REASON_TEXT,
                       CREATED_AT,
                       CREATED_BY
                  from RRL_PICK_WAVE_SHORTAGE
                 where PICK_WAVE_ID = :pick_wave_id
                 order by PICK_WAVE_SHORTAGE_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_wave_audit(self, pick_wave_id: int, limit: int = 200) -> list[dict[str, Any]]:
        params = {"pick_wave_id": pick_wave_id, "limit": min(max(limit, 1), 1000)}
        return self.gateway.fetch_all(
            """
            select *
              from (
                select PICK_WAVE_AUDIT_ID,
                       EVENT_TYPE,
                       MESSAGE_TEXT,
                       PAYLOAD_JSON,
                       CREATED_AT,
                       CREATED_BY
                  from RRL_PICK_WAVE_AUDIT
                 where PICK_WAVE_ID = :pick_wave_id
                 order by PICK_WAVE_AUDIT_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_plans(
        self,
        status: str | None = None,
        customer_order_id: int | None = None,
        customer_id: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if status:
            conditions.append("upper(p.STATUS) = :status")
            params["status"] = status.upper()
        if customer_order_id is not None:
            conditions.append("p.CUSTOMER_ORDER_ID = :customer_order_id")
            params["customer_order_id"] = customer_order_id
        if customer_id is not None:
            conditions.append("p.CUSTOMER_ID = :customer_id")
            params["customer_id"] = customer_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select p.PICK_PLAN_ID,
                       p.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       p.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       p.WARE_ID,
                       p.ROUTE_ID,
                       p.DOCK_ID,
                       p.STATUS,
                       p.PLAN_STRATEGY,
                       p.TOTAL_ORDER_QTY,
                       p.TOTAL_PLANNED_QTY,
                       p.TOTAL_SHORTAGE_QTY,
                       count(distinct l.PICK_PLAN_LINE_ID) LINE_COUNT,
                       count(distinct t.PICK_TASK_ID) TASK_COUNT,
                       count(distinct r.PICK_RESERVATION_ID) ACTIVE_RESERVATION_COUNT,
                       p.CREATED_AT,
                       p.CREATED_BY,
                       p.UPDATED_AT
                  from RRL_PICK_PLAN p
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = p.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = p.CUSTOMER_ID
                  left join RRL_PICK_PLAN_LINE l
                    on l.PICK_PLAN_ID = p.PICK_PLAN_ID
                  left join RRL_PICK_TASK t
                    on t.PICK_PLAN_ID = p.PICK_PLAN_ID
                  left join RRL_PICK_RESERVATION r
                    on r.PICK_PLAN_ID = p.PICK_PLAN_ID
                   and r.RESERVATION_STATUS = 'ACTIVE'
                  {where_sql}
                 group by p.PICK_PLAN_ID,
                          p.CUSTOMER_ORDER_ID,
                          co.ORDER_NO,
                          p.CUSTOMER_ID,
                          c.CUSTOMER_NAME,
                          p.WARE_ID,
                          p.ROUTE_ID,
                          p.DOCK_ID,
                          p.STATUS,
                          p.PLAN_STRATEGY,
                          p.TOTAL_ORDER_QTY,
                          p.TOTAL_PLANNED_QTY,
                          p.TOTAL_SHORTAGE_QTY,
                          p.CREATED_AT,
                          p.CREATED_BY,
                          p.UPDATED_AT
                 order by p.PICK_PLAN_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_plan(self, pick_plan_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select p.PICK_PLAN_ID,
                   p.CUSTOMER_ORDER_ID,
                   co.ORDER_NO,
                   p.CUSTOMER_ID,
                   c.CUSTOMER_NAME,
                   p.WARE_ID,
                   p.ROUTE_ID,
                   p.DOCK_ID,
                   p.STATUS,
                   p.PLAN_STRATEGY,
                   p.TOTAL_ORDER_QTY,
                   p.TOTAL_PLANNED_QTY,
                   p.TOTAL_SHORTAGE_QTY,
                   p.COMMENT_TEXT,
                   p.CREATED_AT,
                   p.CREATED_BY,
                   p.UPDATED_AT,
                   p.UPDATED_BY
              from RRL_PICK_PLAN p
              join RRL_CUSTOMER_ORDER co
                on co.CUSTOMER_ORDER_ID = p.CUSTOMER_ORDER_ID
              left join RRL_CUSTOMER c
                on c.CUSTOMER_ID = p.CUSTOMER_ID
             where p.PICK_PLAN_ID = :pick_plan_id
            """,
            {"pick_plan_id": pick_plan_id},
        )
        if not rows:
            return None

        plan = rows[0]
        plan["lines"] = self.gateway.fetch_all(
            """
            select PICK_PLAN_LINE_ID,
                   CUSTOMER_ORDER_ROW_ID,
                   ARTICUL,
                   PRODUCT_NAME,
                   REQUESTED_QTY,
                   PLANNED_QTY,
                   FULL_PALLET_QTY,
                   CASE_PICK_QTY,
                   SHORTAGE_QTY,
                   STATUS,
                   CREATED_AT,
                   UPDATED_AT
              from RRL_PICK_PLAN_LINE
             where PICK_PLAN_ID = :pick_plan_id
             order by PICK_PLAN_LINE_ID
            """,
            {"pick_plan_id": pick_plan_id},
        )
        plan["tasks"] = self.gateway.fetch_all(
            """
            select PICK_TASK_ID,
                   PICK_PLAN_LINE_ID,
                   TASK_TYPE,
                   STATUS,
                   ARTICUL,
                   PALLET_UID,
                   SSCC,
                   PROD_BATCH_ID,
                   SOURCE_CELL_CODE,
                   TARGET_CELL_CODE,
                   QTY,
                   FACT_QTY,
                   PICK_SEQUENCE,
                   PICK_FACE_ID,
                   PICK_ROUTE_CELL_ID,
                   ASSIGNED_TO,
                   CREATED_AT,
                   STARTED_AT,
                   DONE_AT,
                   DONE_BY,
                   UPDATED_AT,
                   ERROR_TEXT
              from RRL_PICK_TASK
             where PICK_PLAN_ID = :pick_plan_id
             order by PICK_SEQUENCE nulls last, PICK_TASK_ID
            """,
            {"pick_plan_id": pick_plan_id},
        )
        plan["reservations"] = self.list_reservations(pick_plan_id=pick_plan_id, limit=500)
        plan["shortages"] = self.list_shortages(pick_plan_id=pick_plan_id, limit=500)
        plan["decisions"] = self.gateway.fetch_all(
            """
            select PICK_DECISION_ID,
                   PICK_PLAN_LINE_ID,
                   DECISION_TYPE,
                   MESSAGE_TEXT,
                   PAYLOAD_JSON,
                   CREATED_AT,
                   CREATED_BY
              from RRL_PICK_DECISION_LOG
             where PICK_PLAN_ID = :pick_plan_id
             order by PICK_DECISION_ID
            """,
            {"pick_plan_id": pick_plan_id},
        )
        return plan

    def list_reservations(
        self,
        pick_plan_id: int | None = None,
        status: str | None = None,
        customer_order_id: int | None = None,
        pallet_uid: str | None = None,
        articul: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 1000)}
        if pick_plan_id is not None:
            conditions.append("r.PICK_PLAN_ID = :pick_plan_id")
            params["pick_plan_id"] = pick_plan_id
        if status:
            conditions.append("upper(r.RESERVATION_STATUS) = :status")
            params["status"] = status.upper()
        if customer_order_id is not None:
            conditions.append("r.CUSTOMER_ORDER_ID = :customer_order_id")
            params["customer_order_id"] = customer_order_id
        if pallet_uid:
            conditions.append("upper(r.PALLET_UID) = :pallet_uid")
            params["pallet_uid"] = pallet_uid.upper()
        if articul:
            conditions.append("upper(r.ARTICUL) = :articul")
            params["articul"] = articul.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select r.PICK_RESERVATION_ID,
                       r.PICK_PLAN_ID,
                       r.PICK_PLAN_LINE_ID,
                       r.PICK_TASK_ID,
                       r.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       r.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       r.RESERVATION_LEVEL,
                       r.RESERVATION_STATUS,
                       r.RESERVATION_SCOPE,
                       r.PALLET_UID,
                       r.SSCC,
                       r.ARTICUL,
                       r.PROD_BATCH_ID,
                       r.SOURCE_CELL_CODE,
                       r.RESERVED_QTY,
                       r.CREATED_AT,
                       r.CREATED_BY,
                       r.RELEASED_AT,
                       r.CONSUMED_AT,
                       r.UPDATED_AT
                  from RRL_PICK_RESERVATION r
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = r.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = r.CUSTOMER_ID
                  {where_sql}
                 order by r.PICK_RESERVATION_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_routes(self, ware_id: int | None = None, active_only: int | None = None) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if ware_id is not None:
            conditions.append("r.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if active_only is not None and int(active_only) == 1:
            conditions.append("r.ACTIVE = 1")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select r.PICK_ROUTE_ID,
                   r.WARE_ID,
                   w.NAME WARE_NAME,
                   r.ROUTE_CODE,
                   r.ROUTE_NAME,
                   r.ROUTE_KIND,
                   r.ACTIVE,
                   count(distinct rc.PICK_ROUTE_CELL_ID) CELL_COUNT,
                   count(distinct pf.PICK_FACE_ID) PICK_FACE_COUNT,
                   r.CREATED_AT,
                   r.UPDATED_AT
              from RRL_PICK_ROUTE r
              left join RRL_WARES w
                on w.ID = r.WARE_ID
              left join RRL_PICK_ROUTE_CELL rc
                on rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID
              left join RRL_PICK_FACE pf
                on pf.PICK_ROUTE_ID = r.PICK_ROUTE_ID
              {where_sql}
             group by r.PICK_ROUTE_ID,
                      r.WARE_ID,
                      w.NAME,
                      r.ROUTE_CODE,
                      r.ROUTE_NAME,
                      r.ROUTE_KIND,
                      r.ACTIVE,
                      r.CREATED_AT,
                      r.UPDATED_AT
             order by r.WARE_ID, r.ROUTE_CODE
            """,
            params,
        )

    def upsert_route(self, request: PickRouteUpsertRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_route(
                p_pick_route_id => :pick_route_id,
                p_route_code => :route_code,
                p_route_name => :route_name,
                p_ware_id => :ware_id,
                p_route_kind => :route_kind,
                p_active => :active,
                p_updated_by => :updated_by
              );
            end;
            """,
            request.model_dump(),
        )

    def list_route_cells(
        self,
        pick_route_id: int | None = None,
        ware_id: int | None = None,
        active_only: int | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if pick_route_id is not None:
            conditions.append("rc.PICK_ROUTE_ID = :pick_route_id")
            params["pick_route_id"] = pick_route_id
        if ware_id is not None:
            conditions.append("rc.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if active_only is not None and int(active_only) == 1:
            conditions.append("rc.ACTIVE = 1")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select rc.PICK_ROUTE_CELL_ID,
                   rc.PICK_ROUTE_ID,
                   r.ROUTE_CODE,
                   rc.WARE_ID,
                   w.NAME WARE_NAME,
                   rc.CELL_CODE,
                   rc.PICK_SEQUENCE,
                   rc.ZONE_CODE,
                   rc.AISLE_CODE,
                   rc.SIDE_CODE,
                   rc.LEVEL_NO,
                   rc.ACTIVE,
                   rc.CREATED_AT,
                   rc.UPDATED_AT
              from RRL_PICK_ROUTE_CELL rc
              join RRL_PICK_ROUTE r
                on r.PICK_ROUTE_ID = rc.PICK_ROUTE_ID
              left join RRL_WARES w
                on w.ID = rc.WARE_ID
              {where_sql}
             order by rc.WARE_ID, r.ROUTE_CODE, rc.PICK_SEQUENCE, rc.CELL_CODE
            """,
            params,
        )

    def upsert_route_cell(self, request: PickRouteCellUpsertRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_route_cell(
                p_pick_route_cell_id => :pick_route_cell_id,
                p_pick_route_id => :pick_route_id,
                p_cell_code => :cell_code,
                p_pick_sequence => :pick_sequence,
                p_zone_code => :zone_code,
                p_aisle_code => :aisle_code,
                p_side_code => :side_code,
                p_level_no => :level_no,
                p_active => :active,
                p_updated_by => :updated_by
              );
            end;
            """,
            request.model_dump(),
        )

    def list_pick_faces(
        self,
        ware_id: int | None = None,
        articul: str | None = None,
        active_only: int | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if ware_id is not None:
            conditions.append("pf.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if active_only is not None and int(active_only) == 1:
            conditions.append("pf.ACTIVE = 1")
        if articul:
            conditions.append(
                "exists (select 1 from RRL_PICK_FACE_ARTICUL pfa "
                "where pfa.PICK_FACE_ID = pf.PICK_FACE_ID "
                "and upper(pfa.ARTICUL) = :articul and pfa.ACTIVE = 1)"
            )
            params["articul"] = articul.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select pf.PICK_FACE_ID,
                   pf.WARE_ID,
                   w.NAME WARE_NAME,
                   pf.CELL_CODE,
                   pf.PICK_FACE_CODE,
                   pf.PICK_FACE_TYPE,
                   pf.PICK_ROUTE_ID,
                   r.ROUTE_CODE,
                   pf.PICK_ROUTE_CELL_ID,
                   pf.PICK_SEQUENCE,
                   pf.MIN_CASE_QTY,
                   pf.MAX_CASE_QTY,
                   pf.REPLENISHMENT_TRIGGER_QTY,
                   pf.MAX_WEIGHT,
                   pf.MAX_VOLUME,
                   pf.ALLOW_DYNAMIC_ASSIGNMENT,
                   pf.ACTIVE,
                   (select count(*)
                      from RRL_PICK_FACE_ARTICUL pfa
                     where pfa.PICK_FACE_ID = pf.PICK_FACE_ID
                       and pfa.ACTIVE = 1) ARTICUL_COUNT,
                   pf.CREATED_AT,
                   pf.UPDATED_AT
              from RRL_PICK_FACE pf
              left join RRL_WARES w
                on w.ID = pf.WARE_ID
              left join RRL_PICK_ROUTE r
                on r.PICK_ROUTE_ID = pf.PICK_ROUTE_ID
              {where_sql}
             order by pf.WARE_ID, pf.PICK_SEQUENCE nulls last, pf.CELL_CODE, pf.PICK_FACE_ID
            """,
            params,
        )

    def upsert_pick_face(self, request: PickFaceUpsertRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_pick_face(
                p_pick_face_id => :pick_face_id,
                p_ware_id => :ware_id,
                p_cell_code => :cell_code,
                p_pick_face_code => :pick_face_code,
                p_pick_face_type => :pick_face_type,
                p_pick_route_id => :pick_route_id,
                p_pick_route_cell_id => :pick_route_cell_id,
                p_pick_sequence => :pick_sequence,
                p_min_case_qty => :min_case_qty,
                p_max_case_qty => :max_case_qty,
                p_replenishment_trigger_qty => :replenishment_trigger_qty,
                p_max_weight => :max_weight,
                p_max_volume => :max_volume,
                p_allow_dynamic_assignment => :allow_dynamic_assignment,
                p_active => :active,
                p_comment_text => :comment_text,
                p_updated_by => :updated_by
              );
            end;
            """,
            request.model_dump(),
        )

    def list_pick_face_articuls(self, pick_face_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select PICK_FACE_ARTICUL_ID,
                   PICK_FACE_ID,
                   ARTICUL,
                   PRIORITY,
                   MIN_QTY,
                   MAX_QTY,
                   CASE_PICK_ENABLED,
                   USE_ARTICUL_REPLENISH_RULE,
                   REPLENISHMENT_METHOD,
                   REPLENISHMENT_RELEASE_POLICY,
                   REPLENISHMENT_QTY_MODE,
                   MIN_TRIGGER_BOX_QTY,
                   MIN_TRIGGER_LAYER_QTY,
                   SAFETY_LAYER_QTY,
                   BOXES_PER_LAYER,
                   BOXES_PER_PALLET,
                   BOX_VOLUME_M3,
                   ALLOW_PARTIAL_PALLET,
                   PREDICTIVE_BUFFER_MIN,
                   PICK_RATE_SOURCE,
                   RECHECK_ON_PICK_EVENT,
                   ACTIVE,
                   VALID_FROM,
                   VALID_TO,
                   CREATED_AT,
                   UPDATED_AT
              from RRL_PICK_FACE_ARTICUL
             where PICK_FACE_ID = :pick_face_id
             order by PRIORITY, ARTICUL, PICK_FACE_ARTICUL_ID
            """,
            {"pick_face_id": pick_face_id},
        )

    def assign_pick_face_articul(self, request: PickFaceArticulUpsertRequest) -> int:
        from ..modules.inventory.public import configure_existing_pick_face_article
        return configure_existing_pick_face_article(self.gateway,request,request.updated_by or "")

    def list_articul_replenishment_rules(
        self,
        articul: str | None = None,
        active_only: int | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if articul:
            conditions.append("upper(ARTICUL) = :articul")
            params["articul"] = articul.upper()
        if active_only is not None and int(active_only) == 1:
            conditions.append("ACTIVE = 1")
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select ARTICUL_REPLENISH_RULE_ID,
                   ARTICUL,
                   REPLENISHMENT_METHOD,
                   REPLENISHMENT_RELEASE_POLICY,
                   REPLENISHMENT_QTY_MODE,
                   MIN_TRIGGER_BOX_QTY,
                   MIN_TRIGGER_LAYER_QTY,
                   SAFETY_LAYER_QTY,
                   BOXES_PER_LAYER,
                   BOXES_PER_PALLET,
                   BOX_VOLUME_M3,
                   ALLOW_PARTIAL_PALLET,
                   PREDICTIVE_BUFFER_MIN,
                   PICK_RATE_SOURCE,
                   RECHECK_ON_PICK_EVENT,
                   ACTIVE,
                   COMMENT_TEXT,
                   CREATED_AT,
                   UPDATED_AT
              from RRL_ARTICUL_REPLENISH_RULE
              {where_sql}
             order by ARTICUL
            """,
            params,
        )

    def upsert_articul_replenishment_rule(self, request: ArticulReplenishmentRuleUpsertRequest) -> int:
        params = request.model_dump()
        if request.articul_replenish_rule_id is not None:
            self.gateway.execute(
                """
                update RRL_ARTICUL_REPLENISH_RULE
                   set ARTICUL = upper(:articul),
                       REPLENISHMENT_METHOD = upper(nvl(:replenishment_method, 'MINIMAX')),
                       REPLENISHMENT_RELEASE_POLICY = upper(nvl(:replenishment_release_policy, 'LAYER_TRIGGER')),
                       REPLENISHMENT_QTY_MODE = upper(nvl(:replenishment_qty_mode, 'FILL_TO_VOLUME')),
                       MIN_TRIGGER_BOX_QTY = :min_trigger_box_qty,
                       MIN_TRIGGER_LAYER_QTY = :min_trigger_layer_qty,
                       SAFETY_LAYER_QTY = :safety_layer_qty,
                       BOXES_PER_LAYER = :boxes_per_layer,
                       BOXES_PER_PALLET = :boxes_per_pallet,
                       BOX_VOLUME_M3 = :box_volume_m3,
                       ALLOW_PARTIAL_PALLET = case when nvl(:allow_partial_pallet, 1) = 0 then 0 else 1 end,
                       PREDICTIVE_BUFFER_MIN = :predictive_buffer_min,
                       PICK_RATE_SOURCE = upper(nvl(:pick_rate_source, 'MIXED')),
                       RECHECK_ON_PICK_EVENT = case when nvl(:recheck_on_pick_event, 1) = 0 then 0 else 1 end,
                       ACTIVE = case when nvl(:active, 1) = 0 then 0 else 1 end,
                       COMMENT_TEXT = :comment_text,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where ARTICUL_REPLENISH_RULE_ID = :articul_replenish_rule_id
                """,
                params,
            )
            return request.articul_replenish_rule_id

        existing_rows = self.gateway.fetch_all(
            """
            select ARTICUL_REPLENISH_RULE_ID
              from RRL_ARTICUL_REPLENISH_RULE
             where upper(ARTICUL) = upper(:articul)
            """,
            {"articul": request.articul},
        )
        if existing_rows:
            params["articul_replenish_rule_id"] = int(existing_rows[0]["articul_replenish_rule_id"])
            request.articul_replenish_rule_id = params["articul_replenish_rule_id"]
            return self.upsert_articul_replenishment_rule(request)

        rule_id = self.gateway.call_number_plsql(
            "begin select RRL_ART_REPL_RULE_SQ.nextval into :result from dual; end;",
            {},
        )
        params["articul_replenish_rule_id"] = rule_id
        self.gateway.execute(
            """
            insert into RRL_ARTICUL_REPLENISH_RULE (
              ARTICUL_REPLENISH_RULE_ID, ARTICUL, REPLENISHMENT_METHOD,
              REPLENISHMENT_RELEASE_POLICY, REPLENISHMENT_QTY_MODE,
              MIN_TRIGGER_BOX_QTY, MIN_TRIGGER_LAYER_QTY, SAFETY_LAYER_QTY,
              BOXES_PER_LAYER, BOXES_PER_PALLET, BOX_VOLUME_M3,
              ALLOW_PARTIAL_PALLET, PREDICTIVE_BUFFER_MIN, PICK_RATE_SOURCE,
              RECHECK_ON_PICK_EVENT, ACTIVE, COMMENT_TEXT, CREATED_BY, UPDATED_BY
            ) values (
              :articul_replenish_rule_id, upper(:articul), upper(nvl(:replenishment_method, 'MINIMAX')),
              upper(nvl(:replenishment_release_policy, 'LAYER_TRIGGER')), upper(nvl(:replenishment_qty_mode, 'FILL_TO_VOLUME')),
              :min_trigger_box_qty, :min_trigger_layer_qty, :safety_layer_qty,
              :boxes_per_layer, :boxes_per_pallet, :box_volume_m3,
              case when nvl(:allow_partial_pallet, 1) = 0 then 0 else 1 end,
              :predictive_buffer_min, upper(nvl(:pick_rate_source, 'MIXED')),
              case when nvl(:recheck_on_pick_event, 1) = 0 then 0 else 1 end,
              case when nvl(:active, 1) = 0 then 0 else 1 end,
              :comment_text, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
            )
            """,
            params,
        )
        return rule_id

    def list_shortages(self, pick_plan_id: int | None = None, limit: int = 200) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 1000)}
        if pick_plan_id is not None:
            conditions.append("s.PICK_PLAN_ID = :pick_plan_id")
            params["pick_plan_id"] = pick_plan_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select s.PICK_SHORTAGE_ID,
                       s.PICK_PLAN_ID,
                       s.PICK_PLAN_LINE_ID,
                       s.CUSTOMER_ORDER_ID,
                       co.ORDER_NO,
                       s.CUSTOMER_ORDER_ROW_ID,
                       s.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       s.ARTICUL,
                       s.REQUESTED_QTY,
                       s.AVAILABLE_QTY,
                       s.RESERVED_BY_OTHER_QTY,
                       s.PLANNED_QTY,
                       s.SHORTAGE_QTY,
                       s.REASON_CODE,
                       s.REASON_TEXT,
                       s.CREATED_AT,
                       s.CREATED_BY
                  from RRL_PICK_SHORTAGE s
                  join RRL_CUSTOMER_ORDER co
                    on co.CUSTOMER_ORDER_ID = s.CUSTOMER_ORDER_ID
                  left join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = s.CUSTOMER_ID
                  {where_sql}
                 order by s.PICK_SHORTAGE_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )
