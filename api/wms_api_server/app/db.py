from collections.abc import Iterator
from contextlib import contextmanager
import os
import threading
import logging
from typing import Any

import oracledb

from .config import get_settings

# python-oracledb thin mode does not support CL8MSWIN1251 (old Russian Oracle charset).
# If DB uses that charset, Cyrillic VARCHAR2 columns come back as "?????????".
# Setting WMS_ORACLE_THICK_MODE=1 switches to thick mode (requires Oracle Instant Client)
# which respects NLS_LANG and handles any charset correctly.
if os.environ.get("WMS_ORACLE_THICK_MODE", "0") == "1":
    try:
        oracledb.init_oracle_client()
    except Exception:
        pass  # already initialised or client not found — stay in thin mode

_LOG=logging.getLogger(__name__)

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
                getmode=oracledb.POOL_GETMODE_TIMEDWAIT,
                wait_timeout=30000,
            )
        return _pool


@contextmanager
def oracle_connection() -> Iterator[oracledb.Connection]:
    pool = _oracle_pool()
    call_timeout = max(1000, min(120000, int(os.environ.get("WMS_ORACLE_CALL_TIMEOUT_MS", "30000"))))
    connection = pool.acquire()
    connection.call_timeout = call_timeout
    try:
        yield connection
    finally:
        # Oracle package/context state survives SQL rollback and pool release.
        # A failed policy admission must not poison the next independent lease.
        try:
            connection.call_timeout = 3000
            connection.rollback()
            with connection.cursor() as cursor:
                cursor.callproc("RRL_STOCK_POSTING_API.reset_connection")
            pool.release(connection)
        except Exception as exc:
            _LOG.warning("Oracle lease discarded after cleanup failure (%s)",type(exc).__name__)
            try:
                pool.drop(connection)
            except Exception:
                try:
                    connection.close()
                except Exception:
                    pass


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
