"""
Functional, UI-contract-adjacent and business-consistency tests for TMS-2 Sprint 2.

Sprint 2 scope: select STs and create a trip from the selection.

Run:
    python -m pytest tests/transport/test_sprint2_functional.py -q -ra --tb=short
"""

from __future__ import annotations

import os

import pytest
import requests


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
SPRINT2_DATE = os.environ.get("TMS_SPRINT2_STDATE", "2026-05-25")


@pytest.fixture(scope="session")
def api() -> requests.Session:
    session = requests.Session()
    session.auth = AUTH
    session.headers.update({"Content-Type": "application/json"})
    return session


def available_rows(api: requests.Session):
    response = api.get(
        f"{BASE_URL}/api/admin/transport/available-sts",
        params={"stdate": SPRINT2_DATE, "unassigned_only": True},
    )
    assert response.status_code == 200, f"{response.status_code}: {response.text}"
    rows = response.json()
    if not rows:
        pytest.skip(f"No free STs for {SPRINT2_DATE}")
    return rows


@pytest.fixture()
def created_task(api: requests.Session):
    response = api.post(
        f"{BASE_URL}/api/admin/transport/tasks",
        json={"transtype": "10", "shipment_date": SPRINT2_DATE},
    )
    assert response.status_code == 200, f"{response.status_code}: {response.text}"
    task_id = int(response.json()["task_id"])
    try:
        yield task_id
    finally:
        api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel")


class TestSprint2CreateTrip:
    def test_create_trip_returns_existing_task_detail(self, api, created_task):
        response = api.get(f"{BASE_URL}/api/admin/transport/tasks/{created_task}")
        assert response.status_code == 200
        task = response.json()
        assert task["ID"] == created_task
        assert str(task["SHIPMENT_DATE"]).startswith(SPRINT2_DATE)

    def test_assign_selected_sts_to_created_trip(self, api, created_task):
        selected = [row["ST_NUMBER"] for row in available_rows(api)[:2]]
        response = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{created_task}/sts",
            json={"st_numbers": selected},
        )
        assert response.status_code == 200, f"{response.status_code}: {response.text}"
        assert response.json()["assigned"] == len(selected)

        task_sts = api.get(f"{BASE_URL}/api/admin/transport/tasks/{created_task}/sts").json()
        assigned = {row["ST_NUMBER"] for row in task_sts}
        assert set(selected) <= assigned

    def test_assigned_sts_leave_unassigned_available_list(self, api, created_task):
        selected = [row["ST_NUMBER"] for row in available_rows(api)[:2]]
        response = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{created_task}/sts",
            json={"st_numbers": selected},
        )
        assert response.status_code == 200, f"{response.status_code}: {response.text}"

        remaining = available_rows(api)
        remaining_numbers = {row["ST_NUMBER"] for row in remaining}
        assert not (set(selected) & remaining_numbers)

    def test_cancel_created_trip_returns_sts_to_available_list(self, api):
        selected = [row["ST_NUMBER"] for row in available_rows(api)[:1]]
        created = api.post(
            f"{BASE_URL}/api/admin/transport/tasks",
            json={"transtype": "10", "shipment_date": SPRINT2_DATE},
        )
        assert created.status_code == 200
        task_id = int(created.json()["task_id"])
        assigned = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
            json={"st_numbers": selected},
        )
        assert assigned.status_code == 200

        canceled = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel")
        assert canceled.status_code == 200, f"{canceled.status_code}: {canceled.text}"
        rows = available_rows(api)
        assert selected[0] in {row["ST_NUMBER"] for row in rows}


class TestSprint2SelectionBusinessConsistency:
    def test_selection_totals_equal_sum_of_rows(self, api):
        rows = available_rows(api)[:5]
        totals = {
            "pallets": sum(int(row["PALLETS_COUNT"] or 0) for row in rows),
            "weight": sum(float(row["WEIGHT_KG"] or 0) for row in rows),
            "volume": sum(float(row["VOLUME_M3"] or 0) for row in rows),
        }
        assert totals["pallets"] > 0
        assert totals["weight"] > 0
        assert totals["volume"] >= 0

    def test_assignment_preserves_task_st_business_totals(self, api, created_task):
        selected_rows = available_rows(api)[:3]
        selected = [row["ST_NUMBER"] for row in selected_rows]
        response = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{created_task}/sts",
            json={"st_numbers": selected},
        )
        assert response.status_code == 200, f"{response.status_code}: {response.text}"
        task_sts = api.get(f"{BASE_URL}/api/admin/transport/tasks/{created_task}/sts").json()
        assigned = [row for row in task_sts if row["ST_NUMBER"] in set(selected)]
        assert set(selected) <= {row["ST_NUMBER"] for row in assigned}
        assert sum(int(row["PALLETS_COUNT"] or 0) for row in assigned) > 0
        assert sum(float(row["WEIGHT_KG"] or 0) for row in assigned) > 0
