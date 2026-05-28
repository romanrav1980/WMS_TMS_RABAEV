"""
Functional and business-consistency tests for TMS-2 Sprint 1.

Sprint 1 scope: available ST table and filters.

Run:
    python -m pytest tests/transport/test_sprint1_functional.py -q -ra --tb=short
"""

from __future__ import annotations

import os
import time

import pytest
import requests


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
SPRINT1_DATE = os.environ.get("TMS_SPRINT1_STDATE", "2026-05-25")
EMPTY_DATE = "2099-01-01"

REQUIRED_COLUMNS = {
    "ST_NUMBER",
    "ADDR",
    "REGION",
    "RAION",
    "TRANSPORT_TYPE",
    "NEEDS_HYDRO_BOARD",
    "STOL",
    "PRIM1",
    "WARE_ID",
    "NAPR",
    "PALLETS_COUNT",
    "WEIGHT_KG",
    "VOLUME_M3",
    "STDATE",
    "DATE_LOAD",
    "TRANSTASK_ID",
    "VERIFY_PERC",
    "SUGAR",
}


@pytest.fixture(scope="session")
def api() -> requests.Session:
    session = requests.Session()
    session.auth = AUTH
    session.headers.update({"Content-Type": "application/json"})
    return session


def get_available(api: requests.Session, **params):
    response = api.get(f"{BASE_URL}/api/admin/transport/available-sts", params=params)
    assert response.status_code == 200, f"{response.status_code}: {response.text}"
    data = response.json()
    assert isinstance(data, list)
    return data


@pytest.fixture(scope="session")
def sprint1_rows(api: requests.Session):
    rows = get_available(api, stdate=SPRINT1_DATE, unassigned_only=True)
    if not rows:
        pytest.skip(f"No Sprint 1 ST rows for {SPRINT1_DATE}")
    return rows


class TestSprint1AvailableStFunctional:
    def test_available_sts_returns_required_columns(self, sprint1_rows):
        missing = REQUIRED_COLUMNS - set(sprint1_rows[0])
        assert not missing, f"Missing columns: {sorted(missing)}"

    def test_available_sts_uses_legacy_uppercase_keys(self, sprint1_rows):
        assert all(key == key.upper() for key in sprint1_rows[0].keys())

    def test_date_filter_returns_only_requested_date(self, sprint1_rows):
        assert all(str(row["STDATE"]).startswith(SPRINT1_DATE) for row in sprint1_rows)

    def test_unassigned_only_excludes_assigned_sts(self, sprint1_rows):
        assert all(row.get("TRANSTASK_ID") in (None, 0, "0") for row in sprint1_rows)

    def test_empty_future_date_is_fast_and_empty(self, api):
        started = time.perf_counter()
        rows = get_available(api, stdate=EMPTY_DATE, unassigned_only=True)
        elapsed_ms = (time.perf_counter() - started) * 1000
        assert rows == []
        assert elapsed_ms < 2500, f"Empty-date path is too slow: {elapsed_ms:.0f} ms"


class TestSprint1Filters:
    def test_ware_ids_filter(self, api, sprint1_rows):
        ware_id = int(sprint1_rows[0]["WARE_ID"])
        rows = get_available(api, stdate=SPRINT1_DATE, ware_ids=[ware_id], unassigned_only=True)
        assert rows
        assert all(int(row["WARE_ID"]) == ware_id for row in rows)

    def test_addr_mask_filter_matches_addr_region_or_raion(self, api, sprint1_rows):
        sample = sprint1_rows[0]
        token = (sample.get("RAION") or sample.get("REGION") or sample.get("ADDR") or "")[:4]
        if not token:
            pytest.skip("No address token in fixture row")
        rows = get_available(api, stdate=SPRINT1_DATE, addr_mask=token, unassigned_only=True)
        assert rows
        assert all(
            token in (row.get("ADDR") or "")
            or token in (row.get("REGION") or "")
            or token in (row.get("RAION") or "")
            for row in rows
        )

    def test_st_mask_include_and_exclude(self, api, sprint1_rows):
        st_number = sprint1_rows[0]["ST_NUMBER"]
        rows = get_available(api, stdate=SPRINT1_DATE, st_mask=st_number, unassigned_only=True)
        assert rows
        assert all(st_number.lower() in row["ST_NUMBER"].lower() for row in rows)

        excluded = get_available(
            api,
            stdate=SPRINT1_DATE,
            st_mask=st_number,
            st_mask_exclude=True,
            unassigned_only=True,
        )
        assert all(st_number.lower() not in row["ST_NUMBER"].lower() for row in excluded)

    def test_transport_type_filter(self, api, sprint1_rows):
        transport_type = sprint1_rows[0]["TRANSPORT_TYPE"]
        rows = get_available(
            api,
            stdate=SPRINT1_DATE,
            transport_type=transport_type,
            unassigned_only=True,
        )
        assert rows
        assert all(row["TRANSPORT_TYPE"] == transport_type for row in rows)

    def test_max_weight_and_volume_filters(self, api, sprint1_rows):
        max_weight = max(float(row["WEIGHT_KG"] or 0) for row in sprint1_rows[:10]) + 1
        max_volume = max(float(row["VOLUME_M3"] or 0) for row in sprint1_rows[:10]) + 1
        rows = get_available(
            api,
            stdate=SPRINT1_DATE,
            max_weight_kg=max_weight,
            max_volume_m3=max_volume,
            unassigned_only=True,
        )
        assert rows
        assert all(float(row["WEIGHT_KG"] or 0) < max_weight for row in rows)
        assert all(float(row["VOLUME_M3"] or 0) < max_volume for row in rows)


class TestSprint1BusinessConsistency:
    def test_business_numeric_fields_are_non_negative(self, sprint1_rows):
        for row in sprint1_rows:
            assert int(row["PALLETS_COUNT"] or 0) >= 0
            assert float(row["WEIGHT_KG"] or 0) >= 0
            assert float(row["VOLUME_M3"] or 0) >= 0
            assert 0 <= float(row["VERIFY_PERC"] or 0) <= 100
            assert int(row["SUGAR"] or 0) in (0, 1)

    def test_st_number_is_unique_in_response(self, sprint1_rows):
        st_numbers = [row["ST_NUMBER"] for row in sprint1_rows]
        assert len(st_numbers) == len(set(st_numbers))

    def test_pallet_rows_have_positive_business_payload(self, sprint1_rows):
        assert any(int(row["PALLETS_COUNT"] or 0) > 0 for row in sprint1_rows)
        assert any(float(row["WEIGHT_KG"] or 0) > 0 for row in sprint1_rows)
