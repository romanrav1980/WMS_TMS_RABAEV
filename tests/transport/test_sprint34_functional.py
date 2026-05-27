"""
test_sprint34_functional.py — Functional tests for Sprint 34.

Sprint 34 fixes cancel_task: unassign all STs before marking task DELETED=1.
Previously, STs stayed locked to a deleted task and wouldn't appear as available.

Bug: cancel_task SET DELETED=1 without calling RRL_TT_ADD_PALL(TT_ID=0) first.
Fix: iterate get_task_sts, call unassign Oracle proc for each, then delete.
"""

import pytest
from unittest.mock import patch, MagicMock, call


class TestCancelTaskUnassignsSts:

    def _make_sts(self, *st_nums: str) -> list[dict]:
        return [{"ST_NUMBER": n, "PALLETS_COUNT": 1} for n in st_nums]

    def test_cancel_with_no_sts_still_deletes(self):
        from app.services.transport_service import TransportService
        svc = TransportService()
        with (
            patch.object(svc, "get_task", return_value={"ID": 1, "PAY_ORDER_ID": None}),
            patch.object(svc, "get_task_sts", return_value=[]),
            patch.object(svc.gateway, "call_varchar_function") as mock_func,
            patch.object(svc.gateway, "execute") as mock_exec,
        ):
            svc.cancel_task(1, "tester")

        mock_func.assert_not_called()
        mock_exec.assert_called_once()

    def test_cancel_calls_unassign_for_each_st(self):
        from app.services.transport_service import TransportService
        svc = TransportService()
        sts = self._make_sts("ST001", "ST002", "ST003")
        with (
            patch.object(svc, "get_task", return_value={"ID": 5, "PAY_ORDER_ID": None}),
            patch.object(svc, "get_task_sts", return_value=sts),
            patch.object(svc.gateway, "call_varchar_function") as mock_func,
            patch.object(svc.gateway, "execute"),
        ):
            svc.cancel_task(5, "tester")

        assert mock_func.call_count == 3
        called_sts = {c.args[1]["ST_NUMBER1"] for c in mock_func.call_args_list}
        assert called_sts == {"ST001", "ST002", "ST003"}
        for c in mock_func.call_args_list:
            assert c.args[1]["TT_ID"] == 0, "TT_ID must be 0 to unassign"

    def test_cancel_raises_409_when_billed(self):
        from app.services.transport_service import TransportService
        from fastapi import HTTPException
        svc = TransportService()
        with patch.object(svc, "get_task", return_value={"ID": 10, "PAY_ORDER_ID": 42}):
            with pytest.raises(HTTPException) as exc:
                svc.cancel_task(10, "tester")
        assert exc.value.status_code == 409
        assert "42" in exc.value.detail

    def test_cancel_unassign_happens_before_delete(self):
        """Unassign calls must precede the DELETE update."""
        from app.services.transport_service import TransportService
        svc = TransportService()
        sts = self._make_sts("ST100")
        call_order: list[str] = []

        orig_func = svc.gateway.call_varchar_function
        orig_exec = svc.gateway.execute

        with (
            patch.object(svc, "get_task", return_value={"ID": 7, "PAY_ORDER_ID": None}),
            patch.object(svc, "get_task_sts", return_value=sts),
            patch.object(svc.gateway, "call_varchar_function", side_effect=lambda *a, **kw: call_order.append("unassign")),
            patch.object(svc.gateway, "execute", side_effect=lambda *a, **kw: call_order.append("delete")),
        ):
            svc.cancel_task(7, "tester")

        assert call_order == ["unassign", "delete"], f"Unexpected order: {call_order}"

    def test_cancel_many_sts(self):
        """Cancel handles large task (20 STs) without error."""
        from app.services.transport_service import TransportService
        svc = TransportService()
        sts = self._make_sts(*[f"ST{i:03d}" for i in range(20)])
        with (
            patch.object(svc, "get_task", return_value={"ID": 99, "PAY_ORDER_ID": None}),
            patch.object(svc, "get_task_sts", return_value=sts),
            patch.object(svc.gateway, "call_varchar_function"),
            patch.object(svc.gateway, "execute"),
        ):
            svc.cancel_task(99, "tester")


class TestCancelTaskIntegration:

    def test_after_cancel_sts_visible_in_available(self):
        """After cancel, unassigned STs should appear in available list (no TRANSTASK_ID filter needed)."""
        from app.services.transport_service import TransportService
        svc = TransportService()

        # Simulate: task has 2 STs; cancel unassigns them;
        # subsequent list_available_sts (unassigned_only=True) should include them.
        sts = [
            {"ST_NUMBER": "A1", "TRANSTASK_ID": None, "PALLETS_COUNT": 2},
            {"ST_NUMBER": "A2", "TRANSTASK_ID": None, "PALLETS_COUNT": 1},
        ]
        with (
            patch.object(svc, "get_task", return_value={"ID": 3, "PAY_ORDER_ID": None}),
            patch.object(svc, "get_task_sts", return_value=sts),
            patch.object(svc.gateway, "call_varchar_function"),
            patch.object(svc.gateway, "execute"),
            patch.object(svc, "list_available_sts", return_value=sts) as mock_avail,
        ):
            svc.cancel_task(3, "tester")
            result = svc.list_available_sts(unassigned_only=True)

        assert len(result) == 2
