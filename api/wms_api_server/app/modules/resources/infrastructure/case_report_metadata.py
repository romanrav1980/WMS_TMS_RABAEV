"""Exact-task shortage-report boundary with native current authority and shared REV."""
from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any
import oracledb
from ..contracts_case_read import CaseReadError


@contextmanager
def case_short_report_transaction(gateway: Any, task: int, actor: str) -> Iterator[Any]:
    with gateway.transaction("CASE scoped shortage report") as cursor:
        try:
            cursor.callproc("RRL_CASE_REPORT_SCOPE.begin_change", [task, actor])
            yield cursor
        except oracledb.DatabaseError as error:
            code = error.args[0].code
            if code in {20882, 20886, 20860}:
                raise CaseReadError("CASE_SHORT_REPORT_REJECTED", str(error.args[0]).split("\n", 1)[0],
                    403 if code == 20882 else 503 if code == 20860 else 409) from error
            raise
        finally:
            cursor.callproc("RRL_STOCK_METADATA_TX.end_change")
