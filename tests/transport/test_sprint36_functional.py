"""
test_sprint36_functional.py — Functional tests for Sprint 36 (bulk ST removal).

Sprint 36 adds multi-select checkboxes in the trip detail table so the
dispatcher can remove several STs from a trip in one click.

Test scope:
  - Backend: DELETE /tasks/{id}/sts/{st} already exists; bulk = N parallel calls
  - Frontend state logic: selectedTripStNums set management
  - Guard: bulk bar must not show for shipped/billed trips
  - Edge: empty selection → handleBulkUnassign is a no-op
"""

import pytest
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Helpers / fakes
# ---------------------------------------------------------------------------

def make_task(task_id: int = 1, condition: str = "Активен", pay_order_id=None) -> dict:
    return {"ID": task_id, "CONDITION": condition, "PAY_ORDER_ID": pay_order_id}


def make_st(st_number: str, task_id: int = 1) -> dict:
    return {"ST_NUMBER": st_number, "TT_ID": task_id, "ADDRESS": "ул. Тест, 1"}


# ---------------------------------------------------------------------------
# Backend: individual DELETE endpoint (already tested in earlier sprints,
# but sanity-check here as the bulk operation depends on it)
# ---------------------------------------------------------------------------

class TestDeleteStEndpointContract:
    """The bulk removal is N parallel DELETE calls — the endpoint must be idempotent."""

    def test_delete_unassigns_st(self):
        """Removing an ST calls RRL_TT_ADD_PALL with TT_ID=0."""
        from unittest.mock import MagicMock
        gateway = MagicMock()
        gateway.call_varchar_function.return_value = "ok"

        from api.wms_api_server.app.services.transport_service import TransportService
        svc = TransportService.__new__(TransportService)
        svc.gateway = gateway

        # Simulate remove_st_from_task
        with patch.object(svc, "get_task", return_value=make_task()), \
             patch.object(svc, "get_task_sts", return_value=[make_st("ST-001")]):
            svc.remove_st_from_task(task_id=1, st_number="ST-001", user_id="u1")

        gateway.call_varchar_function.assert_called_once_with(
            "RABAEV.RRL_TT_ADD_PALL", {"TT_ID": 0, "ST_NUMBER1": "ST-001"}
        )

    def test_delete_raises_for_shipped_task(self):
        """Cannot remove STs from a shipped trip."""
        from api.wms_api_server.app.services.transport_service import TransportService
        from fastapi import HTTPException

        gateway = MagicMock()
        svc = TransportService.__new__(TransportService)
        svc.gateway = gateway

        with patch.object(svc, "get_task", return_value=make_task(condition="Отгружен")):
            with pytest.raises(HTTPException) as exc_info:
                svc.remove_st_from_task(task_id=1, st_number="ST-001", user_id="u1")
        assert exc_info.value.status_code == 409

    def test_delete_raises_for_billed_task(self):
        """Cannot remove STs from a task that has a billing order."""
        from api.wms_api_server.app.services.transport_service import TransportService
        from fastapi import HTTPException

        gateway = MagicMock()
        svc = TransportService.__new__(TransportService)
        svc.gateway = gateway

        with patch.object(svc, "get_task", return_value=make_task(pay_order_id=42)):
            with pytest.raises(HTTPException) as exc_info:
                svc.remove_st_from_task(task_id=1, st_number="ST-001", user_id="u1")
        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Frontend logic simulation (pure Python — no React runtime needed)
# ---------------------------------------------------------------------------

class DispatchPageSimulator:
    """Minimal simulation of the React state relevant to bulk removal."""

    def __init__(self):
        self.selected_trip_st_nums: set[str] = set()
        self.loading = False
        self.error: str | None = None
        self.unassign_calls: list[str] = []

    def select_task(self, task_id: int):
        """Switching tasks clears the checkbox selection."""
        self.selected_trip_st_nums = set()

    def toggle_check(self, st_num: str):
        if st_num in self.selected_trip_st_nums:
            self.selected_trip_st_nums.discard(st_num)
        else:
            self.selected_trip_st_nums.add(st_num)

    def bulk_bar_visible(self, task: dict) -> bool:
        """Bulk bar is shown only when there's a selection AND task is editable."""
        if not self.selected_trip_st_nums:
            return False
        if task.get("CONDITION") == "Отгружен":
            return False
        if task.get("PAY_ORDER_ID"):
            return False
        return True

    def handle_bulk_unassign(self, task: dict, confirmed: bool = True) -> int:
        """Returns number of unassign calls made."""
        if not self.selected_trip_st_nums:
            return 0
        if not confirmed:
            return 0
        count = len(self.selected_trip_st_nums)
        self.unassign_calls.extend(list(self.selected_trip_st_nums))
        self.selected_trip_st_nums = set()
        return count


class TestFrontendBulkLogic:
    def setup_method(self):
        self.sim = DispatchPageSimulator()

    def test_select_task_clears_selection(self):
        self.sim.selected_trip_st_nums = {"ST-001", "ST-002"}
        self.sim.select_task(task_id=99)
        assert len(self.sim.selected_trip_st_nums) == 0

    def test_toggle_adds_st(self):
        self.sim.toggle_check("ST-001")
        assert "ST-001" in self.sim.selected_trip_st_nums

    def test_toggle_removes_st(self):
        self.sim.selected_trip_st_nums = {"ST-001"}
        self.sim.toggle_check("ST-001")
        assert "ST-001" not in self.sim.selected_trip_st_nums

    def test_bulk_bar_visible_when_selection_and_active(self):
        self.sim.selected_trip_st_nums = {"ST-001"}
        assert self.sim.bulk_bar_visible(make_task(condition="Активен")) is True

    def test_bulk_bar_hidden_when_no_selection(self):
        assert self.sim.bulk_bar_visible(make_task()) is False

    def test_bulk_bar_hidden_for_shipped_task(self):
        self.sim.selected_trip_st_nums = {"ST-001"}
        assert self.sim.bulk_bar_visible(make_task(condition="Отгружен")) is False

    def test_bulk_bar_hidden_for_billed_task(self):
        self.sim.selected_trip_st_nums = {"ST-001"}
        assert self.sim.bulk_bar_visible(make_task(pay_order_id=7)) is False

    def test_bulk_unassign_empty_selection_is_noop(self):
        count = self.sim.handle_bulk_unassign(make_task())
        assert count == 0
        assert self.sim.unassign_calls == []

    def test_bulk_unassign_calls_n_deletes(self):
        self.sim.selected_trip_st_nums = {"ST-001", "ST-002", "ST-003"}
        count = self.sim.handle_bulk_unassign(make_task())
        assert count == 3
        assert len(self.sim.unassign_calls) == 3
        assert set(self.sim.unassign_calls) == {"ST-001", "ST-002", "ST-003"}

    def test_bulk_unassign_clears_selection_after(self):
        self.sim.selected_trip_st_nums = {"ST-001", "ST-002"}
        self.sim.handle_bulk_unassign(make_task())
        assert len(self.sim.selected_trip_st_nums) == 0

    def test_bulk_unassign_cancel_keeps_selection(self):
        self.sim.selected_trip_st_nums = {"ST-001"}
        count = self.sim.handle_bulk_unassign(make_task(), confirmed=False)
        assert count == 0
        assert "ST-001" in self.sim.selected_trip_st_nums

    def test_multi_select_accumulates(self):
        for st in ["ST-A", "ST-B", "ST-C", "ST-D"]:
            self.sim.toggle_check(st)
        assert len(self.sim.selected_trip_st_nums) == 4

    def test_deselect_one_keeps_others(self):
        for st in ["ST-A", "ST-B", "ST-C"]:
            self.sim.toggle_check(st)
        self.sim.toggle_check("ST-B")
        assert self.sim.selected_trip_st_nums == {"ST-A", "ST-C"}
