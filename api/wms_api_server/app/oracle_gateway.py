from typing import Any

import oracledb

from .db import oracle_connection, rows_as_dicts, scalar_to_text


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
            cursor.execute(sql, params or {})
            return rows_as_dicts(cursor)

    def execute(self, sql: str, params: dict[str, Any] | None = None) -> int:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, params or {})
            rowcount = cursor.rowcount
            connection.commit()
            return rowcount

    def execute_many(self, statements: list[tuple[str, dict[str, Any]]]) -> None:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            try:
                for sql, params in statements:
                    cursor.execute(sql, params)
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def call_varchar_function(self, function_name: str, params: dict[str, Any]) -> str:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            result = cursor.callfunc(function_name, oracledb.STRING, keywordParameters=params)
            connection.commit()
            return scalar_to_text(result)

    def call_number_plsql(self, block: str, params: dict[str, Any]) -> int:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            result = cursor.var(oracledb.NUMBER)
            cursor.execute(block, {**params, "result": result})
            connection.commit()
            value = result.getvalue()
            return int(value)

    def execute_plsql(self, block: str, params: dict[str, Any]) -> None:
        with oracle_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(block, params)
            connection.commit()
