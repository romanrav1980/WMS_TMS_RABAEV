"""Explicit gateway bound to the caller's cursor; never commits or opens connections."""
from contextlib import contextmanager
from typing import Any
import oracledb
from .db import rows_as_dicts


class TransactionGateway:
    transaction_bound = True

    def __init__(self, cursor: oracledb.Cursor):
        self.cursor = cursor

    def fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self.cursor.execute(sql, params or {})
        return rows_as_dicts(self.cursor)

    def execute(self, sql: str, params: dict[str, Any] | None = None) -> int:
        self.cursor.execute(sql, params or {})
        return self.cursor.rowcount

    def execute_many(self, statements: list[tuple[str, dict[str, Any]]]) -> None:
        # Preserve dependency order; SQL grouping can reorder business effects.
        for sql, params in statements:
            self.execute(sql, params)

    def execute_plsql(self, block: str, params: dict[str, Any]) -> None:
        self.execute(block, params)

    def call_number_plsql(self, block: str, params: dict[str, Any]) -> int:
        result = self.cursor.var(oracledb.DB_TYPE_NUMBER)
        self.cursor.execute(block, {**params, "result": result})
        return int(result.getvalue())

    @contextmanager
    def transaction(self, operation_name: str):
        # Outer command owns rollback and commit.
        yield self.cursor
