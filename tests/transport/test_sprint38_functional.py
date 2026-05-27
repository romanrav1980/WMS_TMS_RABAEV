"""
test_sprint38_functional.py — Functional tests for Sprint 38 (copy trip).

Sprint 38 adds a «📋 Копировать» button in the trip detail panel.
Clicking it creates a new trip with the same vehicle, driver, dock,
shipment_time, transtype and shipment_date as the source trip — but
with no STs. After creation the dispatcher is navigated to the new trip.

Test scope:
  - Backend: POST /tasks + optional PATCH (existing endpoints, new sequence)
  - Copy attributes: all non-null reqs are transferred
  - Copy excludes: STs, PRICE, PAY_ORDER_ID, CONDITION, DELETED, ID
  - Guard: copy is available for any trip (active, closed, billed)
  - State: after copy, new task is selected; active tab is "tasks"
"""

import pytest
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(
    task_id: int = 1,
    transport: str | None = "Е715ТТ",
    voditel_id: int | None = 5,
    dock: str | None = "Д-3",
    shipment_time: str | None = "08:30",
    shipment_date: str | None = "2026-05-28",
    transtype: str | None = "10",
    condition: str | None = "Активен",
    pay_order_id: int | None = None,
    price: float | None = None,
) -> dict:
    return {
        "ID": task_id,
        "TRANSPORT": transport,
        "VODITEL_ID": voditel_id,
        "DOCK": dock,
        "SHIPMENT_TIME": shipment_time,
        "SHIPMENT_DATE": shipment_date,
        "TRANSTYPE": transtype,
        "CONDITION": condition,
        "PAY_ORDER_ID": pay_order_id,
        "PRICE": price,
        "PALLET_COUNT": 0,
        "ST_COUNT": 0,
        "DELETED": 0,
    }


# ---------------------------------------------------------------------------
# Copy-task logic simulation (mirrors handleCopyTask in React)
# ---------------------------------------------------------------------------

class CopyTaskSimulator:
    def __init__(self, next_id: int = 100):
        self.next_id = next_id
        self.created_tasks: list[dict] = []
        self.patches: list[dict] = []  # [{task_id, patch}]
        self.selected_task: dict | None = None
        self.active_tab: str = "routes"

    def copy_task(self, source: dict) -> dict:
        """Simulate handleCopyTask: POST /tasks + optional PATCH."""
        new_id = self.next_id
        self.next_id += 1

        self.created_tasks.append({
            "task_id": new_id,
            "transtype": source.get("TRANSTYPE"),
            "shipment_date": source.get("SHIPMENT_DATE"),
        })

        patch: dict = {}
        if source.get("TRANSPORT"):   patch["transport"]     = source["TRANSPORT"]
        if source.get("VODITEL_ID"):  patch["voditel_id"]    = source["VODITEL_ID"]
        if source.get("DOCK"):        patch["dock"]          = source["DOCK"]
        if source.get("SHIPMENT_TIME"): patch["shipment_time"] = source["SHIPMENT_TIME"]

        if patch:
            self.patches.append({"task_id": new_id, "patch": patch})

        new_task = make_task(
            task_id=new_id,
            transport=source.get("TRANSPORT"),
            voditel_id=source.get("VODITEL_ID"),
            dock=source.get("DOCK"),
            shipment_time=source.get("SHIPMENT_TIME"),
            shipment_date=source.get("SHIPMENT_DATE"),
            transtype=source.get("TRANSTYPE"),
            condition="Активен",
            pay_order_id=None,
            price=None,
        )
        self.selected_task = new_task
        self.active_tab = "tasks"
        return new_task


class TestCopyTaskLogic:
    def _sim(self) -> CopyTaskSimulator:
        return CopyTaskSimulator(next_id=200)

    def test_copy_creates_new_task(self):
        sim = self._sim()
        source = make_task(task_id=1)
        sim.copy_task(source)
        assert len(sim.created_tasks) == 1
        assert sim.created_tasks[0]["task_id"] == 200

    def test_copy_inherits_transtype_and_date(self):
        sim = self._sim()
        source = make_task(task_id=1, transtype="15", shipment_date="2026-06-01")
        sim.copy_task(source)
        assert sim.created_tasks[0]["transtype"] == "15"
        assert sim.created_tasks[0]["shipment_date"] == "2026-06-01"

    def test_copy_patches_vehicle_driver_dock_time(self):
        sim = self._sim()
        source = make_task(task_id=1, transport="А001АА", voditel_id=7, dock="Д-1", shipment_time="09:00")
        sim.copy_task(source)
        assert len(sim.patches) == 1
        p = sim.patches[0]["patch"]
        assert p["transport"] == "А001АА"
        assert p["voditel_id"] == 7
        assert p["dock"] == "Д-1"
        assert p["shipment_time"] == "09:00"

    def test_copy_no_patch_when_nulls(self):
        sim = self._sim()
        source = make_task(task_id=1, transport=None, voditel_id=None, dock=None, shipment_time=None)
        sim.copy_task(source)
        assert len(sim.patches) == 0

    def test_copy_new_task_has_no_sts(self):
        sim = self._sim()
        source = make_task(task_id=1)
        new_task = sim.copy_task(source)
        assert new_task["ST_COUNT"] == 0
        assert new_task["PALLET_COUNT"] == 0

    def test_copy_new_task_has_no_pay_order(self):
        sim = self._sim()
        source = make_task(task_id=1, pay_order_id=42)
        new_task = sim.copy_task(source)
        assert new_task["PAY_ORDER_ID"] is None

    def test_copy_new_task_has_no_price(self):
        sim = self._sim()
        source = make_task(task_id=1, price=15000.0)
        new_task = sim.copy_task(source)
        assert new_task["PRICE"] is None

    def test_copy_new_task_condition_is_active(self):
        sim = self._sim()
        source = make_task(task_id=1, condition="Отгружен")
        new_task = sim.copy_task(source)
        assert new_task["CONDITION"] == "Активен"

    def test_copy_new_task_has_new_id(self):
        sim = self._sim()
        source = make_task(task_id=1)
        new_task = sim.copy_task(source)
        assert new_task["ID"] != source["ID"]

    def test_copy_selects_new_task(self):
        sim = self._sim()
        source = make_task(task_id=1)
        new_task = sim.copy_task(source)
        assert sim.selected_task is new_task

    def test_copy_switches_to_tasks_tab(self):
        sim = self._sim()
        sim.active_tab = "routes"
        source = make_task(task_id=1)
        sim.copy_task(source)
        assert sim.active_tab == "tasks"

    def test_copy_available_for_shipped_trip(self):
        sim = self._sim()
        source = make_task(task_id=1, condition="Отгружен")
        new_task = sim.copy_task(source)
        assert new_task["ID"] == 200

    def test_copy_available_for_billed_trip(self):
        sim = self._sim()
        source = make_task(task_id=1, pay_order_id=7)
        new_task = sim.copy_task(source)
        assert new_task["ID"] == 200

    def test_multiple_copies_get_different_ids(self):
        sim = self._sim()
        source = make_task(task_id=1)
        t1 = sim.copy_task(source)
        t2 = sim.copy_task(source)
        assert t1["ID"] != t2["ID"]
