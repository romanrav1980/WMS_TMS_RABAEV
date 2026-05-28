"""
test_sprint13_functional.py — Functional completeness tests for Sprint 13.

Sprint 13 scope: vehicle availability + plan-fact
  - GET /vehicles/available returns list with status green/yellow/red
  - GET /plan-fact returns tasks with operations and delta
  - Availability sorted: green first

Run:
    pytest tests/transport/test_sprint13_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
PLAN_DATE = "2026-05-25"
LAST_30 = "2026-05-01"

SHIP_TIME = f"{PLAN_DATE} 09:00"


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def plan_fact_vehicle(api):
    vehicles = api.get(f"{BASE_URL}/api/admin/transport/vehicles")
    if vehicles.status_code != 200 or not vehicles.json():
        pytest.skip("Нет машин")
    vehicle = vehicles.json()[0].get("NUM") or vehicles.json()[0].get("vehicle_num")
    if not vehicle:
        pytest.skip("Нет машины")

    created = api.post(
        f"{BASE_URL}/api/admin/transport/tasks",
        json={"transtype": "Газель", "shipment_date": PLAN_DATE, "vehicle": vehicle},
    )
    if created.status_code not in (200, 201):
        pytest.skip(f"Не удалось создать рейс: {created.status_code} {created.text}")
    task_id = created.json()["task_id"]

    ops_response = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
    if ops_response.status_code != 200 or not ops_response.json():
        pytest.skip(f"Не удалось создать операции: {ops_response.status_code} {ops_response.text}")
    first_op_id = ops_response.json()[0]["op_id"]
    api.patch(
        f"{BASE_URL}/api/admin/transport/operations/{first_op_id}/fact",
        json={"fact_start": "2026-05-25 06:05", "fact_end": "2026-05-25 06:20"},
    )
    return vehicle


# ---------------------------------------------------------------------------
# GET /vehicles/available
# ---------------------------------------------------------------------------

class TestVehiclesAvailable:
    def test_available_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 0})
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_available_is_list(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 0})
        assert isinstance(r.json(), list)

    def test_available_required_fields(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 0})
        data = r.json()
        if not data:
            pytest.skip("Нет машин")
        required = {"vehicle_id", "vehicle_num", "vehicle_type", "marka",
                    "max_pallets", "gidrobort", "free_at", "delay_min",
                    "status", "detail"}
        for item in data:
            missing = required - set(item.keys())
            assert not missing, f"Missing fields: {missing}"

    def test_available_status_values(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 0})
        for item in r.json():
            assert item["status"] in ("green", "yellow", "red"), \
                f"Invalid status: {item['status']}"

    def test_available_sorted_green_first(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 0})
        data = r.json()
        order = {"green": 0, "yellow": 1, "red": 2}
        statuses = [order[d["status"]] for d in data]
        assert statuses == sorted(statuses), "Not sorted green→yellow→red"

    def test_available_missing_shipment_time_422(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"pallets": 0})
        assert r.status_code == 422

    def test_available_with_pallets_filter(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 999})
        assert r.status_code == 200
        for item in r.json():
            if item["max_pallets"] > 0 and item["max_pallets"] < 999:
                assert item["status"] == "red", \
                    f"Vehicle with {item['max_pallets']} pallets should be red for pallets=999"

    def test_available_gidrobort_is_bool(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 0})
        for item in r.json():
            assert isinstance(item["gidrobort"], bool)

    def test_available_delay_min_numeric(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/available",
                    params={"shipment_time": SHIP_TIME, "pallets": 0})
        for item in r.json():
            assert isinstance(item["delay_min"], (int, float))


# ---------------------------------------------------------------------------
# GET /plan-fact
# ---------------------------------------------------------------------------

class TestPlanFact:
    def test_plan_fact_200(self, api, plan_fact_vehicle):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": PLAN_DATE})
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_plan_fact_is_list(self, api, plan_fact_vehicle):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": PLAN_DATE})
        assert isinstance(r.json(), list)

    def test_plan_fact_required_fields(self, api, plan_fact_vehicle):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": PLAN_DATE})
        data = r.json()
        if not data:
            pytest.skip("Нет рейсов за период")
        required = {"tt_id", "vehicle", "shipment_date", "status",
                    "operations", "total_delta_min", "rest_violations"}
        for item in data[:3]:
            missing = required - set(item.keys())
            assert not missing, f"Missing: {missing}"

    def test_plan_fact_operations_is_list(self, api, plan_fact_vehicle):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": PLAN_DATE})
        for item in r.json():
            assert isinstance(item["operations"], list)

    def test_plan_fact_vehicle_filter(self, api, plan_fact_vehicle):
        r_all = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                        params={"date_from": LAST_30, "date_to": PLAN_DATE})
        if not r_all.json():
            pytest.skip("Нет рейсов")
        r_filtered = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                             params={"date_from": LAST_30, "date_to": PLAN_DATE, "vehicle": plan_fact_vehicle})
        assert r_filtered.status_code == 200
        for item in r_filtered.json():
            assert item["vehicle"] == plan_fact_vehicle

    def test_plan_fact_missing_dates_422(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact")
        assert r.status_code == 422

    def test_plan_fact_rest_violations_non_negative(self, api, plan_fact_vehicle):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": PLAN_DATE})
        for item in r.json():
            assert item["rest_violations"] >= 0
