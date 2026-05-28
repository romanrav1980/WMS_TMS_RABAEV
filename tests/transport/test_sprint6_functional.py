"""
test_sprint6_functional.py — Functional completeness tests for Sprint 6.

Sprint 6 scope: pallet detail view for a selected ST
  - GET /sts/{st_number}/pallets returns a list of rows
  - Each row has: PALLET_UID, ZONE, LOAD_TYPE, ORD, ARTICUL, ORDER_WEIGHT,
    PACK_COUNT, ROW_VOLUME_M3
  - LOAD_TYPE is '' | 'Г' | 'П' or null
  - ORDER_WEIGHT >= 0, PACK_COUNT >= 0, ROW_VOLUME_M3 >= 0
  - Rows for the same PALLET_UID share ZONE / LOAD_TYPE / ORD

Run:
    pytest tests/transport/test_sprint6_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date, timedelta


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TOMORROW = os.environ.get("TMS_SPRINT6_STDATE", "2026-05-25")


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


def _get_sample_st(api) -> str | None:
    r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                params={"stdate": TOMORROW})
    if r.status_code != 200 or not r.json():
        return None
    return r.json()[0]["ST_NUMBER"]


# ---------------------------------------------------------------------------
# Endpoint existence and basic structure
# ---------------------------------------------------------------------------

class TestPalletsEndpoint:
    def test_endpoint_returns_200(self, api):
        st = _get_sample_st(api)
        if not st:
            pytest.skip("Нет СТ — проверьте seed 047")
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

    def test_returns_list(self, api):
        st = _get_sample_st(api)
        if not st:
            pytest.skip("Нет СТ")
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_required_fields_present(self, api):
        st = _get_sample_st(api)
        if not st:
            pytest.skip("Нет СТ")
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        data = r.json()
        if not data:
            pytest.skip("СТ без паллет")
        required = {"PALLET_UID", "ZONE", "LOAD_TYPE", "ORD", "ARTICUL",
                    "ORDER_WEIGHT", "PACK_COUNT", "ROW_VOLUME_M3"}
        for row in data[:10]:
            missing = required - set(row.keys())
            assert not missing, f"Отсутствуют поля: {missing} в строке: {row}"

    def test_pallet_uid_not_null(self, api):
        st = _get_sample_st(api)
        if not st:
            pytest.skip("Нет СТ")
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        data = r.json()
        for row in data:
            assert row["PALLET_UID"] is not None, "PALLET_UID должен быть непустым"
            assert len(row["PALLET_UID"]) > 0

    def test_numeric_fields_non_negative(self, api):
        st = _get_sample_st(api)
        if not st:
            pytest.skip("Нет СТ")
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        data = r.json()
        for row in data:
            assert row["ORDER_WEIGHT"] >= 0, f"ORDER_WEIGHT отрицательный: {row}"
            assert row["PACK_COUNT"] >= 0, f"PACK_COUNT отрицательный: {row}"
            assert row["ROW_VOLUME_M3"] >= 0, f"ROW_VOLUME_M3 отрицательный: {row}"

    def test_load_type_valid_values(self, api):
        st = _get_sample_st(api)
        if not st:
            pytest.skip("Нет СТ")
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        data = r.json()
        valid = {None, "", "Г", "П"}
        for row in data:
            assert row["LOAD_TYPE"] in valid, f"Неожиданный LOAD_TYPE: {row['LOAD_TYPE']}"

    def test_rows_within_same_pallet_share_uid_metadata(self, api):
        st = _get_sample_st(api)
        if not st:
            pytest.skip("Нет СТ")
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        data = r.json()
        seen: dict[str, dict] = {}
        for row in data:
            uid = row["PALLET_UID"]
            if uid not in seen:
                seen[uid] = {"ZONE": row["ZONE"], "LOAD_TYPE": row["LOAD_TYPE"], "ORD": row["ORD"]}
            else:
                assert seen[uid]["ZONE"] == row["ZONE"], \
                    f"Паллет {uid}: разные ZONE ({seen[uid]['ZONE']} vs {row['ZONE']})"
                assert seen[uid]["LOAD_TYPE"] == row["LOAD_TYPE"], \
                    f"Паллет {uid}: разные LOAD_TYPE"


# ---------------------------------------------------------------------------
# Multiple pallets per ST
# ---------------------------------------------------------------------------

class TestMultiplePalletsPerSt:
    def test_st_has_multiple_pallets(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        if r.status_code != 200 or not r.json():
            pytest.skip("Нет СТ")
        # Ищем СТ с PALLETS_COUNT > 1
        sts_with_many = [s for s in r.json() if (s.get("PALLETS_COUNT") or 0) > 1]
        if not sts_with_many:
            pytest.skip("Нет СТ с более чем 1 паллетой")
        st = sts_with_many[0]["ST_NUMBER"]
        rp = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        assert rp.status_code == 200
        data = rp.json()
        uids = {row["PALLET_UID"] for row in data}
        assert len(uids) > 1, f"СТ {st} должен иметь >1 паллет, найдено: {uids}"

    def test_pallet_count_matches_available_sts(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        if r.status_code != 200 or not r.json():
            pytest.skip("Нет СТ")
        st_row = r.json()[0]
        st = st_row["ST_NUMBER"]
        expected_pall = st_row.get("PALLETS_COUNT", 0)
        rp = api.get(f"{BASE_URL}/api/admin/transport/sts/{st}/pallets")
        data = rp.json()
        actual_uids = len({row["PALLET_UID"] for row in data})
        assert actual_uids == expected_pall, \
            f"СТ {st}: ожидалось {expected_pall} паллет, получено {actual_uids}"


# ---------------------------------------------------------------------------
# Unknown ST returns empty list (not 404)
# ---------------------------------------------------------------------------

class TestUnknownSt:
    def test_unknown_st_returns_empty(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/sts/НЕСУЩЕСТВУЮЩИЙ_СТ_99999/pallets")
        assert r.status_code == 200
        assert r.json() == []
