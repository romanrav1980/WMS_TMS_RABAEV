from collections.abc import Iterator
from contextlib import contextmanager
import threading
from typing import Any

import oracledb

from .config import get_settings

_pool_lock = threading.Lock()
_pool: oracledb.ConnectionPool | None = None


def _oracle_pool() -> oracledb.ConnectionPool:
    global _pool
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is None:
            settings = get_settings()
            _pool = oracledb.create_pool(
                user=settings.oracle_user,
                password=settings.oracle_password,
                dsn=settings.oracle_dsn,
                min=1,
                max=12,
                increment=1,
                getmode=oracledb.POOL_GETMODE_WAIT,
            )
        return _pool


@contextmanager
def oracle_connection() -> Iterator[oracledb.Connection]:
    pool = _oracle_pool()
    connection = pool.acquire()
    try:
        yield connection
    finally:
        pool.release(connection)


def scalar_to_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def rows_as_dicts(cursor: oracledb.Cursor) -> list[dict[str, Any]]:
    columns = [column[0].lower() for column in cursor.description or []]
    return [dict(zip(columns, [oracle_value(value) for value in row])) for row in cursor.fetchall()]


def oracle_value(value: Any) -> Any:
    if isinstance(value, oracledb.LOB):
        return value.read()
    return value
