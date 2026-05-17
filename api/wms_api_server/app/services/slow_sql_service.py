from typing import Any

from ..oracle_gateway import OracleGateway


class SlowSqlService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_entries(
        self,
        from_log_id: int | None = None,
        to_log_id: int | None = None,
        api_call_id: int | None = None,
        path_like: str | None = None,
        sql_hash: str | None = None,
        min_elapsed_ms: int | None = None,
        error_only: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        where, params = self._filters(
            from_log_id=from_log_id,
            to_log_id=to_log_id,
            api_call_id=api_call_id,
            path_like=path_like,
            sql_hash=sql_hash,
            min_elapsed_ms=min_elapsed_ms,
            error_only=error_only,
        )
        params["limit"] = max(1, min(limit, 500))
        params["offset"] = max(0, offset)
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select q.*, rownum rn
                  from (
                    select LOG_ID, CREATED_AT, MODULE, ACTION, API_CALL_ID,
                           REQUEST_ID, API_METHOD, API_PATH, DB_USER,
                           ELAPSED_MS, SQL_TEXT_HASH, ROW_COUNT, ERROR_TEXT,
                           CLIENT_IDENTIFIER, OPERATION_KIND
                      from RRL_SQL_SLOW_LOG
                     {where}
                     order by LOG_ID desc
                  ) q
                 where rownum <= :offset + :limit
              )
             where rn > :offset
            """,
            params,
        )

    def get_entry(self, log_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select LOG_ID, CREATED_AT, MODULE, ACTION, API_CALL_ID, REQUEST_ID,
                   API_METHOD, API_PATH, DB_USER, ELAPSED_MS, SQL_TEXT_HASH,
                   SQL_TEXT, PARAMS_JSON, ROW_COUNT, ERROR_TEXT,
                   CLIENT_IDENTIFIER, OPERATION_KIND
              from RRL_SQL_SLOW_LOG
             where LOG_ID = :log_id
            """,
            {"log_id": log_id},
        )
        return rows[0] if rows else {}

    def top_entries(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select *
              from (
                select SQL_TEXT_HASH,
                       min(SQL_TEXT) SQL_TEXT_SAMPLE,
                       min(API_PATH) API_PATH_SAMPLE,
                       min(OPERATION_KIND) OPERATION_KIND_SAMPLE,
                       count(*) EXEC_COUNT,
                       round(avg(ELAPSED_MS), 1) AVG_ELAPSED_MS,
                       max(ELAPSED_MS) MAX_ELAPSED_MS,
                       sum(ELAPSED_MS) TOTAL_ELAPSED_MS,
                       max(CREATED_AT) LAST_SEEN_AT
                  from RRL_SQL_SLOW_LOG
                 group by SQL_TEXT_HASH
                 order by max(ELAPSED_MS) desc, count(*) desc
              )
             where rownum <= :limit
            """,
            {"limit": max(1, min(limit, 200))},
        )

    def oracle_top_sql(self, limit: int = 50) -> dict[str, Any]:
        try:
            rows = self.gateway.fetch_all(
                """
                select *
                  from (
                    select SQL_ID,
                           MODULE,
                           ACTION,
                           EXECUTIONS,
                           round(ELAPSED_TIME / 1000) ELAPSED_MS_TOTAL,
                           case when EXECUTIONS > 0
                             then round((ELAPSED_TIME / 1000) / EXECUTIONS, 1)
                             else null
                           end ELAPSED_MS_AVG,
                           BUFFER_GETS,
                           DISK_READS,
                           substr(SQL_TEXT, 1, 1000) SQL_TEXT
                      from v$sql
                     where MODULE like 'WMS_API%'
                     order by ELAPSED_TIME desc
                  )
                 where rownum <= :limit
                """,
                {"limit": max(1, min(limit, 200))},
            )
            return {"available": True, "rows": rows}
        except Exception as exc:
            return {
                "available": False,
                "error": str(exc),
                "hint": "Grant SELECT_CATALOG_ROLE or explicit SELECT on V_$SQL to the Oracle user for native SQL statistics.",
                "rows": [],
            }

    def _filters(
        self,
        from_log_id: int | None,
        to_log_id: int | None,
        api_call_id: int | None,
        path_like: str | None,
        sql_hash: str | None,
        min_elapsed_ms: int | None,
        error_only: int | None,
    ) -> tuple[str, dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if from_log_id is not None:
            conditions.append("LOG_ID >= :from_log_id")
            params["from_log_id"] = from_log_id
        if to_log_id is not None:
            conditions.append("LOG_ID <= :to_log_id")
            params["to_log_id"] = to_log_id
        if api_call_id is not None:
            conditions.append("API_CALL_ID = :api_call_id")
            params["api_call_id"] = api_call_id
        if path_like:
            conditions.append("lower(API_PATH) like lower(:path_like)")
            params["path_like"] = f"%{path_like}%"
        if sql_hash:
            conditions.append("SQL_TEXT_HASH = :sql_hash")
            params["sql_hash"] = sql_hash
        if min_elapsed_ms is not None:
            conditions.append("ELAPSED_MS >= :min_elapsed_ms")
            params["min_elapsed_ms"] = min_elapsed_ms
        if error_only is not None and int(error_only) == 1:
            conditions.append("ERROR_TEXT is not null")
        return (" where " + " and ".join(conditions) if conditions else ""), params
