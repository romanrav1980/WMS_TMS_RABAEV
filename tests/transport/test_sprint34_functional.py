"""
test_sprint34_functional.py — Functional tests for Sprint 34.

Sprint 34 fixes cancel_task: release STs before marking the task deleted.
Current implementation does this set-based in one transaction:
1. SELECT active task and PAY_ORDER_ID.
2. Reject billed task with 409.
3. UPDATE RRL_SBORKA_PALLETS SET TRANSTASK_ID = NULL.
4. UPDATE RRL_TRANSPORT_TASK SET DELETED = 1.
"""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from api.wms_api_server.app.services.transport_service import TransportService


class FakeCursor:
    def __init__(self, row: tuple[int | None] | None = (None,)) -> None:
        self.row = row
        self.calls: list[tuple[str, dict]] = []

    def execute(self, sql: str, params: dict) -> None:
        self.calls.append((sql, params))

    def fetchone(self) -> tuple[int | None] | None:
        return self.row


@contextmanager
def fake_transaction(cursor: FakeCursor):
    yield cursor


class TestCancelTaskUnassignsSts:
    def test_cancel_active_task_unassigns_then_deletes(self):
        svc = TransportService()
        cursor = FakeCursor(row=(None,))
        with patch.object(svc.gateway, "transaction", return_value=fake_transaction(cursor)):
            svc.cancel_task(1, "tester")

        assert len(cursor.calls) == 3
        assert "SELECT PAY_ORDER_ID" in cursor.calls[0][0]
        assert "UPDATE RABAEV.RRL_SBORKA_PALLETS" in cursor.calls[1][0]
        assert "SET TRANSTASK_ID = NULL" in cursor.calls[1][0]
        assert cursor.calls[1][1]["task_id"] == 1
        assert "UPDATE RABAEV.RRL_TRANSPORT_TASK" in cursor.calls[2][0]
        assert "SET DELETED = 1" in cursor.calls[2][0]
        assert cursor.calls[2][1] == {"task_id": 1, "user_id": "tester"}

    def test_cancel_raises_409_when_billed(self):
        svc = TransportService()
        cursor = FakeCursor(row=(42,))
        with patch.object(svc.gateway, "transaction", return_value=fake_transaction(cursor)):
            with pytest.raises(HTTPException) as exc:
                svc.cancel_task(10, "tester")

        assert exc.value.status_code == 409
        assert "42" in exc.value.detail
        assert len(cursor.calls) == 1

    def test_cancel_raises_404_when_task_missing(self):
        svc = TransportService()
        cursor = FakeCursor(row=None)
        with patch.object(svc.gateway, "transaction", return_value=fake_transaction(cursor)):
            with pytest.raises(HTTPException) as exc:
                svc.cancel_task(10, "tester")

        assert exc.value.status_code == 404
        assert len(cursor.calls) == 1

    def test_unassign_happens_before_delete(self):
        svc = TransportService()
        cursor = FakeCursor(row=(0,))
        with patch.object(svc.gateway, "transaction", return_value=fake_transaction(cursor)):
            svc.cancel_task(7, "tester")

        sql_order = [sql for sql, _ in cursor.calls]
        unassign_idx = next(i for i, sql in enumerate(sql_order) if "RRL_SBORKA_PALLETS" in sql)
        delete_idx = next(i for i, sql in enumerate(sql_order) if "RRL_TRANSPORT_TASK" in sql and "SET DELETED" in sql)
        assert unassign_idx < delete_idx

    def test_cache_is_cleared_after_cancel(self):
        svc = TransportService()
        cursor = FakeCursor(row=(None,))
        with (
            patch.object(svc.gateway, "transaction", return_value=fake_transaction(cursor)),
            patch("api.wms_api_server.app.services.transport_service._clear_available_sts_cache") as clear_available,
            patch("api.wms_api_server.app.services.transport_service._clear_task_sts_cache") as clear_task,
        ):
            svc.cancel_task(99, "tester")

        clear_available.assert_called_once_with()
        clear_task.assert_called_once_with(99)


class TestCancelTaskBusinessContract:
    def test_cancel_does_not_call_oracle_when_billed(self):
        svc = TransportService()
        cursor = FakeCursor(row=(123,))
        with patch.object(svc.gateway, "transaction", return_value=fake_transaction(cursor)):
            with pytest.raises(HTTPException):
                svc.cancel_task(3, "tester")

        executed_sql = "\n".join(sql for sql, _ in cursor.calls)
        assert "RRL_SBORKA_PALLETS" not in executed_sql
        assert "SET DELETED = 1" not in executed_sql
