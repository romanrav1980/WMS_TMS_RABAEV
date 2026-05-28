import hashlib
import json
import time
from contextlib import contextmanager
from typing import Any

import oracledb

from .db import oracle_connection, rows_as_dicts, scalar_to_text
from .config import get_settings
from .request_context import get_request_context


class OracleGateway:
    def ping(self) -> dict[str, str]:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                select user user_name,
                       sys_context('USERENV','SERVICE_NAME') service_name,
                       sys_context('USERENV','DB_NAME') db_name
                  from dual
                """
            )
            row = cursor.fetchone()
            return {
                "user_name": scalar_to_text(row[0]),
                "service_name": scalar_to_text(row[1]),
                "db_name": scalar_to_text(row[2]),
            }

    def fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            row_count = 0
            error_text = None
            try:
                cursor.execute(sql, params or {})
                rows = rows_as_dicts(cursor)
                row_count = len(rows)
                return rows
            except Exception as exc:
                error_text = str(exc)
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=sql,
                    params=params or {},
                    started=started,
                    row_count=row_count,
                    error_text=error_text,
                    operation_kind="FETCH_ALL",
                )

    def execute(self, sql: str, params: dict[str, Any] | None = None) -> int:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            rowcount = 0
            error_text = None
            try:
                cursor.execute(sql, params or {})
                rowcount = cursor.rowcount
                connection.commit()
                return rowcount
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=sql,
                    params=params or {},
                    started=started,
                    row_count=rowcount,
                    error_text=error_text,
                    operation_kind="EXECUTE",
                )

    def execute_many(self, statements: list[tuple[str, dict[str, Any]]]) -> None:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            row_count = 0
            error_text = None
            try:
                grouped: dict[str, list[dict[str, Any]]] = {}
                for sql, params in statements:
                    grouped.setdefault(sql, []).append(params)
                for sql, rows in grouped.items():
                    cursor.executemany(sql, rows)
                    row_count += max(cursor.rowcount or 0, 0)
                connection.commit()
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                summary_sql = f"execute_many statements={len(statements)} groups={len(set(sql for sql, _ in statements))}"
                summary_params = {"statement_count": len(statements)}
                self._log_slow_sql(
                    connection=connection,
                    sql=summary_sql,
                    params=summary_params,
                    started=started,
                    row_count=row_count,
                    error_text=error_text,
                    operation_kind="EXECUTE_MANY",
                )

    @contextmanager
    def transaction(self, operation_name: str):
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            error_text = None
            try:
                yield cursor
                connection.commit()
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=operation_name,
                    params={},
                    started=started,
                    row_count=cursor.rowcount if cursor.rowcount is not None else None,
                    error_text=error_text,
                    operation_kind="TRANSACTION",
                )

    def call_varchar_function(self, function_name: str, params: dict[str, Any]) -> str:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            error_text = None
            try:
                result = cursor.callfunc(function_name, oracledb.STRING, keywordParameters=params)
                connection.commit()
                return scalar_to_text(result)
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=f"callfunc {function_name}",
                    params=params,
                    started=started,
                    row_count=None,
                    error_text=error_text,
                    operation_kind="CALL_FUNCTION",
                )

    def call_varchar_plsql(self, block: str, params: dict[str, Any]) -> str:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            error_text = None
            result = cursor.var(oracledb.STRING)
            try:
                cursor.execute(block, {**params, "result": result})
                connection.commit()
                return scalar_to_text(result.getvalue())
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=block,
                    params=params,
                    started=started,
                    row_count=None,
                    error_text=error_text,
                    operation_kind="CALL_VARCHAR_PLSQL",
                )

    def call_number_plsql(self, block: str, params: dict[str, Any]) -> int:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            error_text = None
            result = cursor.var(oracledb.NUMBER)
            try:
                cursor.execute(block, {**params, "result": result})
                connection.commit()
                value = result.getvalue()
                return int(value)
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=block,
                    params=params,
                    started=started,
                    row_count=None,
                    error_text=error_text,
                    operation_kind="CALL_NUMBER_PLSQL",
                )

    def call_optional_number_plsql(self, block: str, params: dict[str, Any]) -> int | None:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            error_text = None
            result = cursor.var(oracledb.NUMBER)
            try:
                cursor.execute(block, {**params, "result": result})
                connection.commit()
                value = result.getvalue()
                return int(value) if value is not None else None
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=block,
                    params=params,
                    started=started,
                    row_count=None,
                    error_text=error_text,
                    operation_kind="CALL_OPTIONAL_NUMBER_PLSQL",
                )

    def execute_plsql(self, block: str, params: dict[str, Any]) -> None:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            self._apply_session_context(cursor)
            started = time.perf_counter()
            error_text = None
            try:
                cursor.execute(block, params)
                connection.commit()
            except Exception as exc:
                error_text = str(exc)
                connection.rollback()
                raise
            finally:
                self._log_slow_sql(
                    connection=connection,
                    sql=block,
                    params=params,
                    started=started,
                    row_count=cursor.rowcount if cursor.rowcount is not None else None,
                    error_text=error_text,
                    operation_kind="EXECUTE_PLSQL",
                )

    def _apply_session_context(self, cursor: oracledb.Cursor) -> None:
        context = get_request_context()
        module = "WMS_API"
        if context and context.api_call_id is not None:
            module = f"WMS_API:{context.api_call_id}"
        action = "BACKGROUND"
        if context and context.method and context.path:
            action = f"{context.method.upper()} {context.path}"
        client_identifier = None
        if context:
            client_identifier = (
                f"api:{context.api_call_id}" if context.api_call_id is not None else f"req:{context.request_id}"
            )
        try:
            cursor.execute(
                """
                begin
                  dbms_application_info.set_module(:module_name, :action_name);
                  dbms_session.set_identifier(:client_identifier);
                end;
                """,
                {
                    "module_name": _truncate(module, 48),
                    "action_name": _truncate(action, 32),
                    "client_identifier": _truncate(client_identifier or "WMS_API", 64),
                },
            )
        except Exception:
            return

    def _log_slow_sql(
        self,
        connection: oracledb.Connection,
        sql: str,
        params: dict[str, Any] | None,
        started: float,
        row_count: int | None,
        error_text: str | None,
        operation_kind: str,
    ) -> None:
        settings = get_settings()
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        if not settings.slow_sql_enabled:
            return
        if elapsed_ms < settings.slow_sql_threshold_ms and error_text is None:
            return

        context = get_request_context()
        sql_text = (sql or "").strip()
        sql_hash = hashlib.sha256(sql_text.encode("utf-8", errors="replace")).hexdigest()
        params_json = _json_dumps_limited(params or {}, settings.slow_sql_max_params_chars)
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                insert into RRL_SQL_SLOW_LOG (
                  LOG_ID, CREATED_AT, MODULE, ACTION, API_CALL_ID, REQUEST_ID,
                  API_METHOD, API_PATH, DB_USER, ELAPSED_MS, SQL_TEXT_HASH,
                  SQL_TEXT, PARAMS_JSON, ROW_COUNT, ERROR_TEXT, CLIENT_IDENTIFIER,
                  OPERATION_KIND
                ) values (
                  RRL_SQL_SLOW_LOG_SQ.nextval, systimestamp, :module_name, :action_name,
                  :api_call_id, :request_id, :api_method, :api_path, user,
                  :elapsed_ms, :sql_text_hash, :sql_text, :params_json,
                  :row_count, :error_text, :client_identifier, :operation_kind
                )
                """,
                {
                    "module_name": _truncate(
                        f"WMS_API:{context.api_call_id}" if context and context.api_call_id is not None else "WMS_API",
                        48,
                    ),
                    "action_name": _truncate(
                        f"{context.method.upper()} {context.path}" if context and context.method and context.path else "BACKGROUND",
                        32,
                    ),
                    "api_call_id": context.api_call_id if context else None,
                    "request_id": context.request_id if context else None,
                    "api_method": context.method if context else None,
                    "api_path": context.path if context else None,
                    "elapsed_ms": elapsed_ms,
                    "sql_text_hash": sql_hash,
                    "sql_text": _truncate(sql_text, settings.slow_sql_max_text_chars),
                    "params_json": params_json,
                    "row_count": row_count,
                    "error_text": _truncate(error_text, 4000) if error_text else None,
                    "client_identifier": _truncate(
                        f"api:{context.api_call_id}" if context and context.api_call_id is not None
                        else f"req:{context.request_id}" if context and context.request_id
                        else "WMS_API",
                        64,
                    ),
                    "operation_kind": operation_kind,
                },
            )
            connection.commit()
        except Exception:
            try:
                connection.rollback()
            except Exception:
                pass


def _truncate(value: Any, max_length: int) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text[:max_length]


def _json_dumps_limited(value: Any, max_length: int) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))
    except TypeError:
        text = json.dumps(str(value), ensure_ascii=False)
    return text[:max_length]
