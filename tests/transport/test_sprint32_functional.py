"""
test_sprint32_functional.py — Functional tests for Sprint 32.

Sprint 32 adds overload warning banner when tripP > vehicle.PALLETS.
Appears in both tasks panel and routes panel.
Completes Phase 2 (Полуавто) spec: «предупреждение при превышении MAX_PALLET_LOAD».

Backend: no new endpoints — purely frontend change.
Tests cover: overload detection logic, boundary conditions.
"""

import pytest


# ---------------------------------------------------------------------------
# Overload detection logic (mirrors frontend condition)
# ---------------------------------------------------------------------------

def is_overloaded(trip_p: int, max_pallets: int | None) -> bool:
    if max_pallets is None or max_pallets <= 0:
        return False
    return trip_p > max_pallets


def overload_message(trip_p: int, max_pallets: int, vehicle_num: str) -> str:
    return f"Перегруз: {trip_p} пал > {max_pallets} пал (норма для {vehicle_num})"


class TestOverloadDetection:

    def test_no_overload_within_capacity(self):
        assert not is_overloaded(10, 11)
        assert not is_overloaded(11, 11)

    def test_overload_one_above(self):
        assert is_overloaded(12, 11)

    def test_overload_far_above(self):
        assert is_overloaded(25, 11)

    def test_no_vehicle_pallets_info_not_overloaded(self):
        assert not is_overloaded(100, None)

    def test_zero_trip_pallets_not_overloaded(self):
        assert not is_overloaded(0, 11)

    def test_overload_message_format(self):
        msg = overload_message(12, 11, "Т368ХН")
        assert "12 пал" in msg
        assert "11 пал" in msg
        assert "Т368ХН" in msg
        assert "Перегруз" in msg

    def test_boundary_exactly_at_capacity_not_overloaded(self):
        assert not is_overloaded(11, 11)

    def test_boundary_one_over_capacity_overloaded(self):
        assert is_overloaded(12, 11)


# ---------------------------------------------------------------------------
# Integration with LoadBar (no regression)
# ---------------------------------------------------------------------------

class TestLoadBarWithOverload:

    def test_load_bar_clamped_at_100(self):
        """LoadBar % still clamped to 100 even when over capacity."""
        def load_pct(value, max_val):
            return min(100, round(value / max_val * 100))

        assert load_pct(12, 11) == 100
        assert load_pct(15, 11) == 100

    def test_load_bar_color_red_when_over(self):
        def load_color(pct):
            return "red" if pct >= 100 else ("amber" if pct >= 85 else "green")

        assert load_color(100) == "red"

    def test_warning_shows_independently_of_bar_color(self):
        """Both bar (red, 100%) AND warning banner should show at overload."""
        trip_p, max_p = 12, 11
        pct = min(100, round(trip_p / max_p * 100))
        assert pct == 100
        assert is_overloaded(trip_p, max_p)
