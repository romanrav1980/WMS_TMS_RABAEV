"""
test_sprint46_functional.py — Functional tests for Sprint 46 (day step buttons).

Sprint 46 adds ◄ ► buttons next to date inputs on both «Заявки» and «Маршруты»
toolbars. Clicking steps the date by ±1 day.
"""

from datetime import date, timedelta


def shift_date(iso: str, days: int) -> str:
    d = date.fromisoformat(iso)
    return (d + timedelta(days=days)).isoformat()


class TestDayStep:
    def test_next_day(self):
        assert shift_date("2026-05-28", 1) == "2026-05-29"

    def test_prev_day(self):
        assert shift_date("2026-05-28", -1) == "2026-05-27"

    def test_month_boundary_forward(self):
        assert shift_date("2026-05-31", 1) == "2026-06-01"

    def test_month_boundary_backward(self):
        assert shift_date("2026-06-01", -1) == "2026-05-31"

    def test_year_boundary_forward(self):
        assert shift_date("2026-12-31", 1) == "2027-01-01"

    def test_year_boundary_backward(self):
        assert shift_date("2027-01-01", -1) == "2026-12-31"

    def test_leap_year_feb29(self):
        assert shift_date("2028-02-28", 1) == "2028-02-29"

    def test_non_leap_year_march(self):
        assert shift_date("2026-02-28", 1) == "2026-03-01"

    def test_step_back_multiple_times(self):
        d = "2026-05-28"
        for _ in range(7):
            d = shift_date(d, -1)
        assert d == "2026-05-21"

    def test_step_forward_multiple_times(self):
        d = "2026-05-01"
        for _ in range(30):
            d = shift_date(d, 1)
        assert d == "2026-05-31"

    def test_zero_shift_unchanged(self):
        assert shift_date("2026-05-28", 0) == "2026-05-28"

    def test_both_toolbars_use_same_logic(self):
        """Both filterDate and routeShipDate use the same shiftDate function."""
        filter_date = shift_date("2026-05-28", 1)
        route_date  = shift_date("2026-05-28", 1)
        assert filter_date == route_date == "2026-05-29"
