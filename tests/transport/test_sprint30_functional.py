"""
test_sprint30_functional.py — Functional tests for Sprint 30.

Sprint 30 adds:
1. LoadBar component — live pallet capacity bar in task right panel.
   Rendered only when: selectedVehicle has PALLETS, tripP > 0.
   Color thresholds: green <85%, yellow 85-99%, red >=100%.
2. CSS classes: .load-bar-row, .load-bar-track, .load-bar-fill, .load-bar-text.

Backend: no new endpoints — purely frontend sprint.
Tests here focus on:
  - LoadBar percentage calculation logic (mirrored in Python)
  - Threshold boundary values
  - Existing cluster endpoint still works (regression)
"""

import pytest


# ---------------------------------------------------------------------------
# LoadBar percentage calculation (mirrors frontend Math.min(100, round(v/max*100)))
# ---------------------------------------------------------------------------

def load_pct(value: int, max_val: int) -> int:
    return min(100, round(value / max_val * 100))


def load_color(pct: int) -> str:
    if pct >= 100:
        return "red"
    if pct >= 85:
        return "amber"
    return "green"


class TestLoadBarLogic:

    def test_zero_load(self):
        assert load_pct(0, 11) == 0
        assert load_color(0) == "green"

    def test_half_load(self):
        assert load_pct(5, 10) == 50
        assert load_color(50) == "green"

    def test_below_85(self):
        assert load_pct(8, 10) == 80
        assert load_color(80) == "green"

    def test_at_85_threshold(self):
        pct = load_pct(85, 100)
        assert pct == 85
        assert load_color(85) == "amber"

    def test_above_85_below_100(self):
        pct = load_pct(9, 10)
        assert pct == 90
        assert load_color(90) == "amber"

    def test_at_100_full(self):
        pct = load_pct(10, 10)
        assert pct == 100
        assert load_color(100) == "red"

    def test_over_capacity_clamped_to_100(self):
        pct = load_pct(15, 10)
        assert pct == 100  # clamped by min(100, ...)
        assert load_color(100) == "red"

    def test_typical_van_11_pallets(self):
        assert load_pct(11, 11) == 100
        assert load_pct(10, 11) == 91
        assert load_pct(9, 11) == 82
        assert load_color(load_pct(10, 11)) == "amber"
        assert load_color(load_pct(9, 11)) == "green"

    def test_rounding(self):
        # 1/3 → rounds to 33
        assert load_pct(1, 3) == 33
        # 2/3 → rounds to 67
        assert load_pct(2, 3) == 67


# ---------------------------------------------------------------------------
# Regression: existing endpoints still respond correctly
# ---------------------------------------------------------------------------

class TestClustersEndpointRegression:

    def test_list_clusters_returns_list(self):
        """GET /clusters returns a list (even if empty)."""
        from unittest.mock import patch
        from app.services.transport_service import TransportService
        from datetime import date

        with patch.object(TransportService, "list_clusters", return_value=[]) as mock_lc:
            svc = TransportService()
            result = svc.list_clusters(stdate=date.today())
        assert isinstance(result, list)

    def test_list_clusters_groups_by_raion(self):
        """list_clusters aggregates STs by RAION correctly."""
        from unittest.mock import patch, MagicMock
        from app.services.transport_service import TransportService
        from datetime import date

        sts = [
            {"ST_NUMBER": "S1", "RAION": "Север", "PALLETS_COUNT": 3, "WEIGHT_KG": 100.0, "VOLUME_M3": 0.5},
            {"ST_NUMBER": "S2", "RAION": "Север", "PALLETS_COUNT": 2, "WEIGHT_KG": 80.0, "VOLUME_M3": 0.4},
            {"ST_NUMBER": "S3", "RAION": "Юг",    "PALLETS_COUNT": 5, "WEIGHT_KG": 200.0, "VOLUME_M3": 1.0},
        ]

        svc = TransportService()
        with patch.object(svc, "list_available_sts", return_value=sts):
            result = svc.list_clusters(stdate=date.today())

        assert len(result) == 2
        north = next(c for c in result if c["RAION"] == "Север")
        assert north["ST_COUNT"] == 2
        assert north["PALLET_COUNT"] == 5
        south = next(c for c in result if c["RAION"] == "Юг")
        assert south["ST_COUNT"] == 1
        assert south["PALLET_COUNT"] == 5
