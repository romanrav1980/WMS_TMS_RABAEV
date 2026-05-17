from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import oracledb

from .config import get_settings


@contextmanager
def oracle_connection() -> Iterator[oracledb.Connection]:
    settings = get_settings()
    connection = oracledb.connect(
        user=settings.oracle_user,
        password=settings.oracle_password,
        dsn=settings.oracle_dsn,
    )
    try:
        yield connection
    finally:
        connection.close()


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
