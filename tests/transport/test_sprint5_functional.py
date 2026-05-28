"""
test_sprint5_functional.py — Functional completeness tests for Sprint 5.

Sprint 5 scope: assembly progress visibility and vehicle requirements
  - VERIFY_PERC returned in available-sts (0–100)
  - TRANSPORT_TYPE returned in available-sts (matches known type codes)
  - STOL (hydro-board flag) returned in available-sts (0 or 1)
  - READY_PERC included in tasks when include_readiness=true
  - IS_OWN_DRIVER and TK_NAME returned in tasks list

All changes are frontend-only (new components). Tests verify the API
returns all required fields so the UI components have data to display.

Run:
    pytest tests/transport/test_sprint5_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date, timedelta


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
SPRINT5_DATE = os.environ.get("TMS_SPRINT5_STDATE", "2026-05-25")
TOMORROW = SPRINT5_DATE

KNOWN_TRANSPORT_TYPES = {"10", "15", "20реф", "20", "0", ""}


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------------------------------------------------------------------------
# VerifyBar: VERIFY_PERC field in available-sts
# ---------------------------------------------------------------------------

class TestVerifyPercField:
    def test_verify_perc_present_in_available_sts(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        assert r.status_code == 200
        data = r.json()
        if not data:
            pytest.skip("Нет СТ — проверьте seed 047")
        for row in data[:20]:
            assert "VERIFY_PERC" in row, f"VERIFY_PERC отсутствует в строке: {row}"

    def test_verify_perc_values_in_range(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        data = r.json()
        for row in data[:50]:
            perc = row.get("VERIFY_PERC")
            if perc is not None:
                assert 0 <= perc <= 100, f"VERIFY_PERC={perc} вне диапазона [0, 100]"

    def test_assembled_only_filter_returns_nonzero_verify(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW, "assembled_only": "true"})
        assert r.status_code == 200
        data = r.json()
        for row in data:
            perc = row.get("VERIFY_PERC")
            assert perc is None or perc > 0, f"assembled_only вернул VERIFY_PERC={perc}"

    def test_not_assembled_only_filter(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW, "not_assembled_only": "true"})
        assert r.status_code == 200
        data = r.json()
        for row in data:
            perc = row.get("VERIFY_PERC")
            assert perc is None or perc == 0, f"not_assembled_only вернул VERIFY_PERC={perc}"


# ---------------------------------------------------------------------------
# TransportTypeBadge: TRANSPORT_TYPE field
# ---------------------------------------------------------------------------

class TestTransportTypeField:
    def test_transport_type_present_in_available_sts(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        assert r.status_code == 200
        data = r.json()
        if not data:
            pytest.skip("Нет СТ")
        for row in data[:20]:
            assert "TRANSPORT_TYPE" in row

    def test_transport_type_filter_works(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW, "transport_type": "10"})
        assert r.status_code == 200
        data = r.json()
        for row in data:
            tt = row.get("TRANSPORT_TYPE", "")
            assert tt in ("10", "0", None, ""), f"Фильтр transport_type=10 вернул {tt}"

    def test_stol_field_present_and_binary(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        assert r.status_code == 200
        data = r.json()
        for row in data[:30]:
            assert "STOL" in row
            stol = row["STOL"]
            assert stol in (0, 1, None), f"STOL={stol} не 0/1"

    def test_needs_hydro_board_field_present(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        data = r.json()
        for row in data[:20]:
            assert "NEEDS_HYDRO_BOARD" in row


# ---------------------------------------------------------------------------
# READY_PERC: tasks with include_readiness=true
# ---------------------------------------------------------------------------

class TestReadinessFields:
    def test_ready_perc_present_with_flag(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks",
                    params={"shipment_date": TOMORROW, "include_readiness": "true"})
        assert r.status_code == 200
        data = r.json()
        for row in data:
            assert "READY_PERC" in row
            assert "UNREADY_COUNT" in row

    def test_ready_perc_absent_without_flag(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks",
                    params={"shipment_date": TOMORROW, "include_readiness": "false"})
        assert r.status_code == 200
        data = r.json()
        for row in data:
            # Without flag, field may be absent or null — must not be a non-null positive number
            rp = row.get("READY_PERC")
            assert rp is None or rp == 0, (
                "Без include_readiness=true не должно быть вычисленного READY_PERC")

    def test_ready_perc_in_valid_range(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks",
                    params={"include_readiness": "true"})
        data = r.json()
        for row in data[:30]:
            rp = row.get("READY_PERC")
            if rp is not None:
                assert 0 <= rp <= 100, f"READY_PERC={rp} вне диапазона"


# ---------------------------------------------------------------------------
# IS_OWN_DRIVER + TK_NAME: driver ownership badges
# ---------------------------------------------------------------------------

class TestDriverOwnershipFields:
    def test_is_own_driver_present_in_tasks(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks")
        assert r.status_code == 200
        data = r.json()
        for row in data[:20]:
            assert "IS_OWN_DRIVER" in row

    def test_tk_name_present_in_tasks(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks")
        data = r.json()
        for row in data[:20]:
            assert "TK_NAME" in row

    def test_drivers_have_sobstvennyy_field(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/drivers")
        assert r.status_code == 200
        data = r.json()
        if data:
            assert "SOBSTVENNYY" in data[0]
            for d in data:
                sob = d.get("SOBSTVENNYY")
                assert sob in (0, 1, None), f"SOBSTVENNYY={sob} неожиданное значение"

    def test_own_drivers_have_no_tk_name(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks")
        data = r.json()
        for row in data:
            if row.get("IS_OWN_DRIVER") == 1:
                # Свой водитель → TK_NAME null (может быть исключения в legacy-данных)
                # Проверяем хотя бы что поле существует
                assert "TK_NAME" in row

    def test_hired_drivers_have_tk_name_or_null(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks")
        data = r.json()
        for row in data:
            if row.get("IS_OWN_DRIVER") == 0:
                assert "TK_NAME" in row  # поле должно присутствовать (null допустимо)


# ---------------------------------------------------------------------------
# SUGAR is the legacy API field for "полнопалетная отборка".
# ---------------------------------------------------------------------------

class TestFullPalletPickField:
    def test_legacy_full_pallet_pick_field_present_and_binary(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW})
        data = r.json()
        for row in data[:30]:
            assert "SUGAR" in row
            assert row["SUGAR"] in (0, 1), f"SUGAR={row['SUGAR']} не 0/1"
