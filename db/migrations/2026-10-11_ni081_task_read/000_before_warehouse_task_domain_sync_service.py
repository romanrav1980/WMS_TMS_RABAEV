from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from .mes_service import clamp_limit

SUPPORTED_SYNC_TARGETS = {
    ("MANUAL", "PUTAWAY", "WAREHOUSE_HU"),
    ("WAVE", "REPLENISHMENT", "PICK_WAVE"),
    ("WAVE", "PICKING_MOVE", "PICK_WAVE"),
    ("MES_RAW_SUPPLY", "RAW_TO_PRODUCTION", "PRODUCTION_ORDER"),
    ("MES_COMPLETION", "FG_TO_STORAGE", "PRODUCTION_ORDER"),
}

class WarehouseTaskDomainSyncService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def _explicit_sync(self, task_id: int) -> dict[str, Any]:
        state = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if not state or state[0]["state"] != "ACTIVE":
            raise HTTPException(503, detail={"code": "STOCK_RELEASE_NOT_ACTIVE"})
        # The coordinator writes physical fact, domain state and SYNCED atomically.
        # A retry reads that fact; it never applies the legacy effect a second time.
        rows = self.gateway.fetch_all(
            """
            select s.*
              from RRL_WAREHOUSE_TASK_SYNC s
              join RRL_WAREHOUSE_TASK t on t.TASK_ID=s.TASK_ID
             where s.TASK_ID=:id and s.SYNC_STATUS='SYNCED' and t.STATUS='DONE'
               and (exists (
                 select 1 from RRL_WAREHOUSE_TASK_STOCK_MOVE m
                 join RRL_STOCK_OPERATION o on o.OPERATION_ID=m.OPERATION_ID
                 where m.TASK_ID=s.TASK_ID and o.STATE='APPLIED'
                   and o.COMMAND_TYPE='TASK_COMPLETE'
                   and m.QTY=t.FACT_QTY
                   and m.UID_PALLET=nvl(t.UID_PALLET,t.SSCC)
                   and m.FROM_CELL=t.FROM_CELL and m.TO_CELL=t.TO_CELL
               ) or (t.TASK_SOURCE='MANUAL' and t.TASK_TYPE='PUTAWAY' and t.SOURCE_DOC_TYPE='WAREHOUSE_HU'
                 and t.UNIT_CODE='HU' and t.FACT_QTY=1 and exists(
                   select 1 from RRL_STOCK_OPERATION o where o.STATE='APPLIED'
                    and o.OPERATION_ID=json_value(t.COMPLETION_JSON,'$.operation_id')
                    and ((o.COMMAND_TYPE='HU_TASK_COMPLETE'
                      and json_value(o.RESULT_JSON,'$.task_id' returning number)=t.TASK_ID
                      and json_value(o.RESULT_JSON,'$.pallet_identifier')=t.UID_PALLET
                      and json_value(o.RESULT_JSON,'$.cell')=t.TO_CELL
                      and json_value(o.CANONICAL_REQUEST,'$.metadata.scanned_from_cell')=t.FROM_CELL)
                     or(o.COMMAND_TYPE in('HU_RELOCATE_SLOT','HU_REPACK_SLOT') and t.FROM_CELL=t.TO_CELL
                      and json_value(o.RESULT_JSON,'$.task_id' returning number)=t.TASK_ID
                      and json_value(o.RESULT_JSON,'$.pallet_identifier')=t.UID_PALLET
                      and json_value(o.RESULT_JSON,'$.cell')=t.TO_CELL
                      and json_value(o.CANONICAL_REQUEST,'$.metadata.scan_cell')=t.TO_CELL)
                     or(o.COMMAND_TYPE='HU_UNPACK' and t.FROM_CELL=t.TO_CELL
                      and json_value(o.CANONICAL_REQUEST,'$.metadata.scan_cell')=t.TO_CELL
                      and((json_value(o.RESULT_JSON,'$.parent_task_id' returning number)=t.TASK_ID
                        and json_value(o.RESULT_JSON,'$.parent.root')=t.UID_PALLET)
                       or(json_value(o.RESULT_JSON,'$.child_task_id' returning number)=t.TASK_ID
                        and json_value(o.RESULT_JSON,'$.child.root')=t.UID_PALLET))))
                  )))
             order by s.SYNC_ID desc fetch first 1 rows only
            """,
            {"id": task_id},
        )
        if rows:
            return rows[0]
        raise HTTPException(409, detail={"code": "TASK_POSTING_REQUIRED", "task_id": task_id})
    def is_supported(self, task: dict[str, Any]) -> bool:
        return self._target_key(task) in SUPPORTED_SYNC_TARGETS

    def dispatch_after_complete(self, task_id: int, updated_by: str | None = None) -> dict[str, Any] | None:
        task = self._get_task(task_id)
        if not self.is_supported(task):
            return None
        return self._explicit_sync(task_id)

    def retry_task_sync(self, task_id: int, updated_by: str | None = None) -> dict[str, Any]:
        return self._explicit_sync(task_id)

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

    def _target_key(self, task: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
        return (
            str(task.get("task_source") or "").upper(),
            str(task.get("task_type") or "").upper(),
            str(task.get("source_doc_type") or "").upper(),
        )

    def _normalize(self, value: Any) -> str:
        return str(value or "").strip().upper()

