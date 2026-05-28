"""
Functional and business-consistency tests for TMS-2 Sprint 3.

Sprint 3 scope: Routes tab list and trip composition.

Run:
    python -m pytest tests/transport/test_sprint3_functional.py -q -ra --tb=short
"""

from __future__ import annotations

import os

import pytest
import requests


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
SPRINT3_DATE = os.environ.get("TMS_SPRINT3_STDATE", "2026-05-25")

TASK_COLUMNS = {
    "ID",
    "TRANSTYPE",
    "SHIPMENT_DATE",
    "TRANSPORT",
    "VODITEL_NAME",
    "DOCK",
    "TEMP_REGION",
    "REGIONS",
    "PRICE",
    "CONDITION",
    "PALLET_COUNT",
    "ST_COUNT",
    "VOLUME_M3",
    "TK_NAME",
    "LOGIST",
    "PAY_ORDER_ID",
}

TASK_ST_COLUMNS = {
    "ST_NUMBER",
    "ADDR",
    "REGION",
    "RAION",
    "ORD",
    "PALLETS_COUNT",
    "WEIGHT_KG",
    "STDATE",
    "ZONE",
    "TIME_FROM",
    "TIME_TO",
    "LOAD_TYPE",
    "WARE_ID",
    "VERIFY_PERC",
}


@pytest.fixture(scope="session")
def api() -> requests.Session:
    session = requests.Session()
    session.auth = AUTH
    session.headers.update({"Content-Type": "application/json"})
    return session


def get_available(api: requests.Session, limit: int = 2):
    response = api.get(
        f"{BASE_URL}/api/admin/transport/available-sts",
        params={"stdate": SPRINT3_DATE, "unassigned_only": True},
    )
    assert response.status_code == 200, f"{response.status_code}: {response.text}"
    rows = response.json()
    if len(rows) < limit:
        pytest.skip(f"Need at least {limit} free ST rows for Sprint 3")
    return rows[:limit]


@pytest.fixture()
def task_with_sts(api: requests.Session):
    selected = [row["ST_NUMBER"] for row in get_available(api, 2)]
    created = api.post(
        f"{BASE_URL}/api/admin/transport/tasks",
        json={"transtype": "10", "shipment_date": SPRINT3_DATE},
    )
    assert created.status_code == 200, f"{created.status_code}: {created.text}"
    task_id = int(created.json()["task_id"])
    assigned = api.post(
        f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts",
        json={"st_numbers": selected},
    )
    assert assigned.status_code == 200, f"{assigned.status_code}: {assigned.text}"
    try:
        yield task_id, selected
    finally:
        api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/cancel")


class TestSprint3RoutesApi:
    def test_tasks_list_contains_route_columns(self, api, task_with_sts):
        task_id, _ = task_with_sts
        response = api.get(
            f"{BASE_URL}/api/admin/transport/tasks",
            params={"shipment_date": SPRINT3_DATE, "include_readiness": True},
        )
        assert response.status_code == 200, f"{response.status_code}: {response.text}"
        tasks = response.json()
        task = next((row for row in tasks if row["ID"] == task_id), None)
        assert task is not None
        missing = TASK_COLUMNS - set(task)
        assert not missing, f"Missing task columns: {sorted(missing)}"

    def test_route_filters_by_task_id(self, api, task_with_sts):
        task_id, _ = task_with_sts
        response = api.get(
            f"{BASE_URL}/api/admin/transport/tasks",
            params={"task_id": task_id, "include_readiness": True},
        )
        assert response.status_code == 200, f"{response.status_code}: {response.text}"
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["ID"] == task_id

    def test_task_sts_contains_composition_columns(self, api, task_with_sts):
        task_id, selected = task_with_sts
        response = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts")
        assert response.status_code == 200, f"{response.status_code}: {response.text}"
        rows = response.json()
        assert set(selected) <= {row["ST_NUMBER"] for row in rows}
        missing = TASK_ST_COLUMNS - set(rows[0])
        assert not missing, f"Missing composition columns: {sorted(missing)}"


class TestSprint3BusinessConsistency:
    def test_task_counts_match_composition(self, api, task_with_sts):
        task_id, _ = task_with_sts
        task = api.get(
            f"{BASE_URL}/api/admin/transport/tasks",
            params={"task_id": task_id, "include_readiness": True},
        ).json()[0]
        composition = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts").json()
        assert task["ST_COUNT"] == len({row["ST_NUMBER"] for row in composition})
        assert int(task["PALLET_COUNT"] or 0) == sum(int(row["PALLETS_COUNT"] or 0) for row in composition)

    def test_note_patch_is_visible_in_route_detail(self, api, task_with_sts):
        task_id, _ = task_with_sts
        note = "Sprint 3 route note"
        patched = api.patch(f"{BASE_URL}/api/admin/transport/tasks/{task_id}", json={"primechanie": note})
        assert patched.status_code == 200, f"{patched.status_code}: {patched.text}"
        detail = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}").json()
        assert detail["PRIMECHANIE"] == note

