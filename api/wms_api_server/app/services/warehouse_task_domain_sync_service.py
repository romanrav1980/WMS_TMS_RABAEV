from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import MesApplyWmsRequest, MesRawTransferTaskConfirmRequest
from .mes_service import MesService, clamp_limit


SUPPORTED_SYNC_TARGETS = {
    ("WAVE", "REPLENISHMENT", "PICK_WAVE"),
    ("WAVE", "PICKING_MOVE", "PICK_WAVE"),
    ("MES_RAW_SUPPLY", "RAW_TO_PRODUCTION", "PRODUCTION_ORDER"),
    ("MES_COMPLETION", "FG_TO_STORAGE", "PRODUCTION_ORDER"),
}


class WarehouseTaskDomainSyncService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def is_supported(self, task: dict[str, Any]) -> bool:
        return self._target_key(task) in SUPPORTED_SYNC_TARGETS

    def dispatch_after_complete(self, task_id: int, updated_by: str | None = None) -> dict[str, Any] | None:
        task = self._get_task(task_id)
        if not self.is_supported(task):
            return None
        sync = self._ensure_sync_row(task, updated_by)
        return self._run_sync(sync["sync_id"], updated_by)

    def retry_task_sync(self, task_id: int, updated_by: str | None = None) -> dict[str, Any]:
        sync = self.get_task_sync(task_id)
        if not sync:
            task = self._get_task(task_id)
            if not self.is_supported(task):
                raise HTTPException(status_code=400, detail="Warehouse task has no supported domain sync handler.")
            sync = self._ensure_sync_row(task, updated_by)
        if sync.get("sync_status") == "SYNCED":
            return sync
        return self._run_sync(int(sync["sync_id"]), updated_by)

    def get_task_sync(self, task_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_TASK_SYNC
             where TASK_ID = :task_id
             order by SYNC_ID desc
            """,
            {"task_id": task_id},
        )
        return rows[0] if rows else None

    def list_sync(
        self,
        status: str | None = None,
        task_source: str | None = None,
        source_doc_type: str | None = None,
        source_doc_id: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if status:
            conditions.append("SYNC_STATUS = :status")
            params["status"] = status.upper()
        if task_source:
            conditions.append("TASK_SOURCE = :task_source")
            params["task_source"] = task_source.upper()
        if source_doc_type:
            conditions.append("SOURCE_DOC_TYPE = :source_doc_type")
            params["source_doc_type"] = source_doc_type.upper()
        if source_doc_id is not None:
            conditions.append("SOURCE_DOC_ID = :source_doc_id")
            params["source_doc_id"] = source_doc_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select SYNC_ID, TASK_ID, TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE,
                       SOURCE_DOC_ID, SOURCE_TASK_ID, SOURCE_MOVEMENT_ID,
                       SYNC_KEY, SYNC_STATUS, SYNC_ATTEMPT, LAST_ERROR,
                       CREATED_AT, UPDATED_AT, SYNCED_AT, UPDATED_BY
                  from RRL_WAREHOUSE_TASK_SYNC
                  {where_sql}
                 order by case SYNC_STATUS
                            when 'ERROR' then 1
                            when 'RETRY_PENDING' then 2
                            when 'PENDING' then 3
                            when 'IN_PROGRESS' then 4
                            else 9
                          end,
                          nvl(UPDATED_AT, CREATED_AT) desc,
                          SYNC_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def _run_sync(self, sync_id: int, updated_by: str | None) -> dict[str, Any]:
        sync = self._get_sync(sync_id)
        task = self._get_task(int(sync["task_id"]))
        if not self.is_supported(task):
            return self._mark_error(sync_id, "No domain sync handler for this warehouse task.", updated_by)
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK_SYNC
               set SYNC_STATUS = 'IN_PROGRESS',
                   SYNC_ATTEMPT = SYNC_ATTEMPT + 1,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:updated_by, 1, 100),
                   LAST_ERROR = null
             where SYNC_ID = :sync_id
            """,
            {"sync_id": sync_id, "updated_by": updated_by or "API"},
        )
        try:
            target = self._target_key(task)
            if target == ("WAVE", "REPLENISHMENT", "PICK_WAVE"):
                self._sync_wave_replenishment(task, updated_by)
            elif target == ("WAVE", "PICKING_MOVE", "PICK_WAVE"):
                self._sync_wave_picking_move(task, updated_by)
            elif target == ("MES_RAW_SUPPLY", "RAW_TO_PRODUCTION", "PRODUCTION_ORDER"):
                self._sync_mes_raw_supply(task, updated_by)
            elif target == ("MES_COMPLETION", "FG_TO_STORAGE", "PRODUCTION_ORDER"):
                self._sync_mes_completion_storage(task, updated_by)
            else:
                raise ValueError("No domain sync handler for this warehouse task.")
        except Exception as exc:
            return self._mark_error(sync_id, str(exc), updated_by)
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK_SYNC
               set SYNC_STATUS = 'SYNCED',
                   UPDATED_AT = systimestamp,
                   SYNCED_AT = systimestamp,
                   UPDATED_BY = substr(:updated_by, 1, 100),
                   LAST_ERROR = null
             where SYNC_ID = :sync_id
            """,
            {"sync_id": sync_id, "updated_by": updated_by or "API"},
        )
        return self._get_sync(sync_id)

    def _sync_wave_replenishment(self, task: dict[str, Any], updated_by: str | None) -> None:
        source_task_id = task.get("source_task_id")
        if source_task_id is None:
            raise ValueError("Wave replenishment task is missing SOURCE_TASK_ID.")
        rows = self.gateway.fetch_all(
            """
            select count(*) ACTIVE_COUNT
              from RRL_WAREHOUSE_TASK
             where TASK_SOURCE = 'WAVE'
               and TASK_TYPE = 'REPLENISHMENT'
               and SOURCE_DOC_TYPE = 'PICK_WAVE'
               and SOURCE_TASK_ID = :source_task_id
               and STATUS not in ('DONE', 'CANCELLED')
            """,
            {"source_task_id": source_task_id},
        )
        active_count = int(rows[0].get("active_count") or 0) if rows else 0
        wave_status = "IN_PROGRESS" if active_count > 0 else "DONE"
        self._apply_wave_replenishment_stock_move(task, updated_by)
        if wave_status == "DONE":
            self.gateway.execute(
                """
                update RRL_STOCK_RESERVATION
                   set STATUS = 'CONSUMED',
                       CONSUMED_AT = systimestamp,
                       CONSUMED_BY = substr(:updated_by, 1, 100)
                 where RESERVATION_ID = (
                   select SOURCE_RESERVATION_ID
                     from RRL_PICK_WAVE_REPLENISH_TASK
                    where PICK_WAVE_REPLENISH_TASK_ID = :source_task_id
                 )
                   and STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
                """,
                {"source_task_id": source_task_id, "updated_by": updated_by or "API"},
            )
        self.gateway.execute(
            """
            update RRL_PICK_WAVE_REPLENISH_TASK
               set STATUS = :status,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where PICK_WAVE_REPLENISH_TASK_ID = :source_task_id
            """,
            {
                "source_task_id": source_task_id,
                "status": wave_status,
                "updated_by": updated_by or "API",
            },
        )
        if wave_status == "DONE":
            rows = self.gateway.fetch_all(
                """
                select PICK_WAVE_ID
                  from RRL_PICK_WAVE_REPLENISH_TASK
                 where PICK_WAVE_REPLENISH_TASK_ID = :source_task_id
                """,
                {"source_task_id": source_task_id},
            )
            if rows:
                from ..schemas import PickWaveActionRequest
                from .picking_service import PickingService

                PickingService(self.gateway).release_minimax_replenishment(
                    int(rows[0]["pick_wave_id"]),
                    PickWaveActionRequest(updated_by=updated_by or "API"),
                )

    def _apply_wave_replenishment_stock_move(self, task: dict[str, Any], updated_by: str | None) -> None:
        task_id = int(task["task_id"])
        rows = self.gateway.fetch_all(
            """
            select count(*) MOVE_COUNT
              from RRL_WAREHOUSE_TASK_STOCK_MOVE
             where TASK_ID = :task_id
            """,
            {"task_id": task_id},
        )
        if rows and int(rows[0].get("move_count") or 0) > 0:
            return

        uid_pallet = task.get("uid_pallet") or task.get("sscc")
        from_cell = task.get("from_cell")
        to_cell = task.get("to_cell")
        qty = self._to_float(task.get("fact_qty") or task.get("qty"))
        if not uid_pallet:
            raise ValueError("Wave replenishment stock move is missing pallet identifier.")
        if not from_cell or not to_cell:
            raise ValueError("Wave replenishment stock move is missing source or target cell.")
        if qty <= 0:
            raise ValueError("Wave replenishment stock move quantity must be positive.")

        rows = self.gateway.fetch_all(
            """
            select nvl(REMAIN, 0) REMAIN
              from RRL_REMAINS
             where UID_POLETA = :uid_pallet
               and CELL = :from_cell
            """,
            {"uid_pallet": uid_pallet, "from_cell": from_cell},
        )
        source_qty = self._to_float(rows[0].get("remain")) if rows else 0.0
        if source_qty + 0.000001 < qty:
            raise ValueError(
                "Wave replenishment stock move has insufficient source stock: "
                f"{uid_pallet} at {from_cell}, available {source_qty}, required {qty}."
            )

        self.gateway.execute_many(
            [
                (
                    """
                    update RRL_REMAINS
                       set REMAIN = REMAIN - :qty
                     where UID_POLETA = :uid_pallet
                       and CELL = :from_cell
                    """,
                    {"uid_pallet": uid_pallet, "from_cell": from_cell, "qty": qty},
                ),
                (
                    """
                    merge into RRL_REMAINS d
                    using (
                      select :uid_pallet UID_POLETA,
                             :to_cell CELL,
                             :qty REMAIN
                        from dual
                    ) s
                    on (d.UID_POLETA = s.UID_POLETA and d.CELL = s.CELL)
                    when matched then update set
                      d.REMAIN = nvl(d.REMAIN, 0) + s.REMAIN
                    when not matched then insert (UID_POLETA, CELL, REMAIN)
                    values (s.UID_POLETA, s.CELL, s.REMAIN)
                    """,
                    {"uid_pallet": uid_pallet, "to_cell": to_cell, "qty": qty},
                ),
                (
                    """
                    insert into RRL_WAREHOUSE_TASK_STOCK_MOVE (
                      STOCK_MOVE_ID, TASK_ID, TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE,
                      SOURCE_DOC_ID, SOURCE_TASK_ID, UID_PALLET, FROM_CELL, TO_CELL,
                      QTY, CREATED_AT, CREATED_BY
                    ) values (
                      RRL_WH_TASK_STOCK_MOVE_SQ.nextval, :task_id, :task_source, :task_type,
                      :source_doc_type, :source_doc_id, :source_task_id, :uid_pallet,
                      :from_cell, :to_cell, :qty, systimestamp, substr(:created_by, 1, 100)
                    )
                    """,
                    {
                        "task_id": task_id,
                        "task_source": task.get("task_source"),
                        "task_type": task.get("task_type"),
                        "source_doc_type": task.get("source_doc_type"),
                        "source_doc_id": task.get("source_doc_id"),
                        "source_task_id": task.get("source_task_id"),
                        "uid_pallet": uid_pallet,
                        "from_cell": from_cell,
                        "to_cell": to_cell,
                        "qty": qty,
                        "created_by": updated_by or task.get("assigned_to") or "API",
                    },
                ),
            ]
        )

    def _sync_wave_picking_move(self, task: dict[str, Any], updated_by: str | None) -> None:
        source_task_id = task.get("source_task_id")
        if source_task_id is None:
            raise ValueError("Wave picking move task is missing SOURCE_TASK_ID.")
        rows = self.gateway.fetch_all(
            """
            select wt.PICK_WAVE_TASK_ID,
                   wt.PICK_TASK_ID,
                   wt.STATUS,
                   wt.TASK_TYPE
              from RRL_PICK_WAVE_TASK wt
             where wt.PICK_WAVE_TASK_ID = :source_task_id
            """,
            {"source_task_id": source_task_id},
        )
        if not rows:
            raise ValueError("Linked wave task was not found for PICKING_MOVE.")
        wave_task = rows[0]
        if wave_task.get("task_type") != "FULL_PALLET":
            raise ValueError("PICKING_MOVE is supported only for FULL_PALLET wave tasks.")

        rows = self.gateway.fetch_all(
            """
            select count(*) ACTIVE_COUNT
              from RRL_WAREHOUSE_TASK
             where TASK_SOURCE = 'WAVE'
               and TASK_TYPE = 'PICKING_MOVE'
               and SOURCE_DOC_TYPE = 'PICK_WAVE'
               and SOURCE_TASK_ID = :source_task_id
               and STATUS not in ('DONE', 'CANCELLED')
            """,
            {"source_task_id": source_task_id},
        )
        active_count = int(rows[0].get("active_count") or 0) if rows else 0
        wave_status = "IN_PROGRESS" if active_count > 0 else "DONE"
        actor = updated_by or task.get("assigned_to") or "API"
        self.gateway.execute(
            """
            update RRL_PICK_WAVE_TASK
               set STATUS = :status,
                   FACT_QTY = :fact_qty,
                   DONE_AT = case when :status = 'DONE' then sysdate else DONE_AT end,
                   DONE_BY = case when :status = 'DONE' then substr(:updated_by, 1, 50) else DONE_BY end,
                   TARGET_CELL_CODE = nvl(:to_cell, TARGET_CELL_CODE),
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where PICK_WAVE_TASK_ID = :source_task_id
            """,
            {
                "source_task_id": source_task_id,
                "status": wave_status,
                "fact_qty": task.get("fact_qty") or task.get("qty"),
                "to_cell": task.get("to_cell"),
                "updated_by": actor,
            },
        )
        if wave_status == "DONE":
            self.gateway.execute(
                """
                update RRL_PICK_TASK
                   set STATUS = 'DONE',
                       FACT_QTY = :fact_qty,
                       DONE_AT = sysdate,
                       DONE_BY = substr(:updated_by, 1, 50),
                       TARGET_CELL_CODE = nvl(:to_cell, TARGET_CELL_CODE),
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where PICK_TASK_ID = :pick_task_id
                """,
                {
                    "pick_task_id": wave_task.get("pick_task_id"),
                    "fact_qty": task.get("fact_qty") or task.get("qty"),
                    "to_cell": task.get("to_cell"),
                    "updated_by": actor,
                },
            )
            self.gateway.execute(
                """
                update RRL_PICK_RESERVATION
                   set RESERVATION_STATUS = 'CONSUMED',
                       CONSUMED_AT = sysdate,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where PICK_TASK_ID = :pick_task_id
                   and RESERVATION_STATUS = 'ACTIVE'
                """,
                {"pick_task_id": wave_task.get("pick_task_id"), "updated_by": actor},
            )
            self.gateway.execute(
                """
                update RRL_PICK_WAVE_RESERVATION
                   set RESERVATION_STATUS = 'CONSUMED',
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where PICK_TASK_ID = :pick_task_id
                   and RESERVATION_STATUS = 'HARD'
                """,
                {"pick_task_id": wave_task.get("pick_task_id"), "updated_by": actor},
            )

    def _sync_mes_raw_supply(self, task: dict[str, Any], updated_by: str | None) -> None:
        source_task_id = task.get("source_task_id")
        if source_task_id is None:
            raise ValueError("MES raw supply task is missing SOURCE_TASK_ID.")

        raw_task = MesService(self.gateway).get_raw_transfer_task_or_404(int(source_task_id))
        if raw_task.get("task_status") == "DONE":
            return
        if raw_task.get("task_status") == "CANCELLED":
            raise ValueError("MES raw transfer task is cancelled.")

        rows = self.gateway.fetch_all(
            """
            select sum(case when STATUS = 'DONE' then nvl(FACT_QTY, QTY) else 0 end) DONE_QTY,
                   sum(case when STATUS not in ('DONE', 'CANCELLED') then 1 else 0 end) ACTIVE_COUNT
              from RRL_WAREHOUSE_TASK
             where TASK_SOURCE = 'MES_RAW_SUPPLY'
               and TASK_TYPE = 'RAW_TO_PRODUCTION'
               and SOURCE_DOC_TYPE = 'PRODUCTION_ORDER'
               and SOURCE_TASK_ID = :source_task_id
            """,
            {"source_task_id": source_task_id},
        )
        done_qty = float(rows[0].get("done_qty") or 0) if rows else 0
        active_count = int(rows[0].get("active_count") or 0) if rows else 0
        if done_qty <= 0:
            raise ValueError("MES raw supply sync has no completed warehouse quantity.")

        actor = updated_by or task.get("assigned_to") or "API"
        if active_count > 0:
            self.gateway.execute(
                """
                update RRL_MES_RAW_TRANSFER_TASK
                   set TASK_STATUS = 'IN_PROGRESS',
                       FACT_QTY = :done_qty,
                       LAST_ERROR = null
                 where TASK_ID = :source_task_id
                   and TASK_STATUS in ('PLANNED', 'IN_PROGRESS')
                """,
                {"source_task_id": source_task_id, "done_qty": done_qty},
            )
            return

        MesService(self.gateway).confirm_raw_transfer_task(
            int(source_task_id),
            MesRawTransferTaskConfirmRequest(fact_qty=done_qty, confirmed_by=str(actor)),
            sync_warehouse_task=False,
        )

    def _sync_mes_completion_storage(self, task: dict[str, Any], updated_by: str | None) -> None:
        source_movement_id = task.get("source_movement_id")
        if source_movement_id is None:
            raise ValueError("Finished-goods storage task is missing SOURCE_MOVEMENT_ID.")

        movement = self._get_mes_movement(int(source_movement_id))
        if movement.get("movement_type") != "FG_PALLET_RELEASE":
            raise ValueError("Finished-goods storage task is not linked to FG_PALLET_RELEASE.")
        if movement.get("status") == "CANCELLED":
            raise ValueError("FG_PALLET_RELEASE movement is cancelled.")

        expected_pallets = {self._normalize(task.get("uid_pallet")), self._normalize(task.get("sscc"))}
        actual_pallets = {self._normalize(movement.get("uid_pallet")), self._normalize(movement.get("sscc"))}
        expected_pallets.discard("")
        actual_pallets.discard("")
        if expected_pallets and actual_pallets and not expected_pallets.intersection(actual_pallets):
            raise ValueError("FG storage task pallet does not match linked MES movement.")

        target_cell = task.get("to_cell") or movement.get("target_location") or "FG_RECEIVE"
        actor = updated_by or task.get("assigned_to") or "API"
        if movement.get("status") == "APPLIED_TO_WMS":
            if self._normalize(movement.get("target_location")) != self._normalize(target_cell):
                raise ValueError(
                    "FG_PALLET_RELEASE is already applied to WMS with another target location; manual correction is required."
                )
            self.gateway.execute(
                """
                update RRL_MES_MOVEMENT
                   set UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50),
                       LAST_ERROR = null
                 where MOVEMENT_ID = :movement_id
                """,
                {"movement_id": source_movement_id, "updated_by": actor},
            )
            return

        self.gateway.execute(
            """
            update RRL_MES_MOVEMENT
               set TARGET_LOCATION = :target_location,
                   LAST_ERROR = null,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where MOVEMENT_ID = :movement_id
               and MOVEMENT_TYPE = 'FG_PALLET_RELEASE'
            """,
            {
                "movement_id": source_movement_id,
                "target_location": target_cell,
                "updated_by": actor,
            },
        )
        production_order_id = movement.get("production_order_id") or task.get("production_order_id")
        if production_order_id is None:
            raise ValueError("FG storage task is missing PRODUCTION_ORDER_ID.")
        MesService(self.gateway).apply_wms(
            int(production_order_id),
            MesApplyWmsRequest(applied_by=str(actor)),
        )

    def _ensure_sync_row(self, task: dict[str, Any], updated_by: str | None) -> dict[str, Any]:
        sync_key = self._sync_key(task)
        self.gateway.execute(
            """
            merge into RRL_WAREHOUSE_TASK_SYNC d
            using (
              select :sync_key SYNC_KEY,
                     :task_id TASK_ID,
                     :task_source TASK_SOURCE,
                     :task_type TASK_TYPE,
                     :source_doc_type SOURCE_DOC_TYPE,
                     :source_doc_id SOURCE_DOC_ID,
                     :source_task_id SOURCE_TASK_ID,
                     :source_movement_id SOURCE_MOVEMENT_ID,
                     substr(:updated_by, 1, 100) UPDATED_BY
                from dual
            ) s
            on (d.SYNC_KEY = s.SYNC_KEY)
            when matched then update set
              d.SYNC_STATUS = case when d.SYNC_STATUS = 'SYNCED' then d.SYNC_STATUS else 'RETRY_PENDING' end,
              d.UPDATED_AT = systimestamp,
              d.UPDATED_BY = s.UPDATED_BY
            when not matched then insert (
              SYNC_ID, TASK_ID, TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE,
              SOURCE_DOC_ID, SOURCE_TASK_ID, SOURCE_MOVEMENT_ID, SYNC_KEY,
              SYNC_STATUS, SYNC_ATTEMPT, CREATED_AT, UPDATED_BY
            ) values (
              RRL_WH_TASK_SYNC_SQ.nextval, s.TASK_ID, s.TASK_SOURCE, s.TASK_TYPE,
              s.SOURCE_DOC_TYPE, s.SOURCE_DOC_ID, s.SOURCE_TASK_ID,
              s.SOURCE_MOVEMENT_ID, s.SYNC_KEY, 'PENDING', 0,
              systimestamp, s.UPDATED_BY
            )
            """,
            {
                "sync_key": sync_key,
                "task_id": task.get("task_id"),
                "task_source": task.get("task_source"),
                "task_type": task.get("task_type"),
                "source_doc_type": task.get("source_doc_type"),
                "source_doc_id": task.get("source_doc_id"),
                "source_task_id": task.get("source_task_id"),
                "source_movement_id": task.get("source_movement_id"),
                "updated_by": updated_by or "API",
            },
        )
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_TASK_SYNC
             where SYNC_KEY = :sync_key
            """,
            {"sync_key": sync_key},
        )
        return rows[0]

    def _mark_error(self, sync_id: int, error_text: str, updated_by: str | None) -> dict[str, Any]:
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TASK_SYNC
               set SYNC_STATUS = 'ERROR',
                   LAST_ERROR = substr(:error_text, 1, 2000),
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:updated_by, 1, 100)
             where SYNC_ID = :sync_id
            """,
            {"sync_id": sync_id, "error_text": error_text, "updated_by": updated_by or "API"},
        )
        return self._get_sync(sync_id)

    def _get_sync(self, sync_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_TASK_SYNC
             where SYNC_ID = :sync_id
            """,
            {"sync_id": sync_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Warehouse task sync row not found.")
        return rows[0]

    def _get_task(self, task_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_TASK
             where TASK_ID = :task_id
            """,
            {"task_id": task_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Warehouse task not found.")
        return rows[0]

    def _get_mes_movement(self, movement_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_MES_MOVEMENT
             where MOVEMENT_ID = :movement_id
            """,
            {"movement_id": movement_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="MES movement not found.")
        return rows[0]

    def _target_key(self, task: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
        return (
            str(task.get("task_source") or "").upper(),
            str(task.get("task_type") or "").upper(),
            str(task.get("source_doc_type") or "").upper(),
        )

    def _sync_key(self, task: dict[str, Any]) -> str:
        return f"WT:{task.get('task_id')}:{task.get('task_source')}:{task.get('task_type')}:{task.get('source_task_id') or ''}:{task.get('source_movement_id') or ''}"

    def _normalize(self, value: Any) -> str:
        return str(value or "").strip().upper()

    def _to_float(self, value: Any) -> float:
        if value is None:
            return 0.0
        return float(value)
