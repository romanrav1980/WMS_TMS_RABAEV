"""
test_sprint39_functional.py — Functional tests for Sprint 39.

Sprint 39 adds to the right filter panel:
  1. Active-filter badge showing count of currently active filters
  2. «× Сбросить» button that resets all filters to defaults in one click

Test scope — pure state logic simulation:
  - activeFilterCount counts exactly which filters deviate from default
  - handleResetFilters resets every filter to its default
  - badge is hidden when count == 0
  - reset button is hidden when count == 0
"""


# ---------------------------------------------------------------------------
# Simulate filter state and helpers
# ---------------------------------------------------------------------------

DEFAULT_FILTERS = {
    "addr_mask": "",
    "st_mask": "",
    "st_mask_exclude": False,
    "assembled_only": False,
    "not_assembled_only": False,
    "unassigned_only": True,   # True = default (НЕ РАСПРЕДЕЛЁННЫЕ включён)
    "date_to": "",
    "max_weight_kg": None,
    "max_vol_m3": None,
    "tr_type_filter": "",
    "articul_filter": "",
}


def active_filter_count(filters: dict) -> int:
    """Mirror the activeFilterCount computed value in React."""
    return sum([
        bool(filters["addr_mask"]),
        bool(filters["st_mask"]),
        filters["st_mask_exclude"],
        filters["assembled_only"],
        filters["not_assembled_only"],
        not filters["unassigned_only"],   # non-default = True if unchecked
        bool(filters["date_to"]),
        filters["max_weight_kg"] is not None,
        filters["max_vol_m3"] is not None,
        bool(filters["tr_type_filter"]),
        bool(filters["articul_filter"]),
    ])


def reset_filters() -> dict:
    return dict(DEFAULT_FILTERS)


# ---------------------------------------------------------------------------
# Tests: activeFilterCount
# ---------------------------------------------------------------------------

class TestActiveFilterCount:
    def test_defaults_count_is_zero(self):
        assert active_filter_count(DEFAULT_FILTERS) == 0

    def test_addr_mask_counts(self):
        f = {**DEFAULT_FILTERS, "addr_mask": "Лысьва"}
        assert active_filter_count(f) == 1

    def test_st_mask_counts(self):
        f = {**DEFAULT_FILTERS, "st_mask": "ST-001"}
        assert active_filter_count(f) == 1

    def test_st_mask_exclude_counts(self):
        f = {**DEFAULT_FILTERS, "st_mask_exclude": True}
        assert active_filter_count(f) == 1

    def test_assembled_only_counts(self):
        f = {**DEFAULT_FILTERS, "assembled_only": True}
        assert active_filter_count(f) == 1

    def test_not_assembled_only_counts(self):
        f = {**DEFAULT_FILTERS, "not_assembled_only": True}
        assert active_filter_count(f) == 1

    def test_unassigned_only_false_counts(self):
        # Default is True; disabling it is a non-default = counts
        f = {**DEFAULT_FILTERS, "unassigned_only": False}
        assert active_filter_count(f) == 1

    def test_unassigned_only_true_does_not_count(self):
        f = {**DEFAULT_FILTERS, "unassigned_only": True}
        assert active_filter_count(f) == 0

    def test_date_to_counts(self):
        f = {**DEFAULT_FILTERS, "date_to": "2026-06-01"}
        assert active_filter_count(f) == 1

    def test_max_weight_counts(self):
        f = {**DEFAULT_FILTERS, "max_weight_kg": 5000}
        assert active_filter_count(f) == 1

    def test_max_weight_none_does_not_count(self):
        f = {**DEFAULT_FILTERS, "max_weight_kg": None}
        assert active_filter_count(f) == 0

    def test_max_vol_counts(self):
        f = {**DEFAULT_FILTERS, "max_vol_m3": 12.5}
        assert active_filter_count(f) == 1

    def test_tr_type_counts(self):
        f = {**DEFAULT_FILTERS, "tr_type_filter": "10"}
        assert active_filter_count(f) == 1

    def test_articul_counts(self):
        f = {**DEFAULT_FILTERS, "articul_filter": "ART-007"}
        assert active_filter_count(f) == 1

    def test_multiple_filters_sum(self):
        f = {**DEFAULT_FILTERS,
             "addr_mask": "Пермь",
             "assembled_only": True,
             "tr_type_filter": "15",
             "max_weight_kg": 3000}
        assert active_filter_count(f) == 4

    def test_all_filters_active(self):
        f = {
            "addr_mask": "x",
            "st_mask": "y",
            "st_mask_exclude": True,
            "assembled_only": True,
            "not_assembled_only": True,
            "unassigned_only": False,
            "date_to": "2026-06-01",
            "max_weight_kg": 1000,
            "max_vol_m3": 5.0,
            "tr_type_filter": "20реф",
            "articul_filter": "Z",
        }
        assert active_filter_count(f) == 11


# ---------------------------------------------------------------------------
# Tests: reset_filters
# ---------------------------------------------------------------------------

class TestResetFilters:
    def test_reset_clears_addr_mask(self):
        f = {**DEFAULT_FILTERS, "addr_mask": "Лысьва"}
        assert reset_filters()["addr_mask"] == ""

    def test_reset_restores_unassigned_only_to_true(self):
        f = {**DEFAULT_FILTERS, "unassigned_only": False}
        assert reset_filters()["unassigned_only"] is True

    def test_reset_clears_max_weight(self):
        assert reset_filters()["max_weight_kg"] is None

    def test_reset_clears_max_vol(self):
        assert reset_filters()["max_vol_m3"] is None

    def test_reset_count_is_zero(self):
        assert active_filter_count(reset_filters()) == 0

    def test_reset_returns_full_defaults(self):
        assert reset_filters() == DEFAULT_FILTERS


# ---------------------------------------------------------------------------
# Tests: badge/button visibility
# ---------------------------------------------------------------------------

class TestBadgeVisibility:
    def test_badge_hidden_at_zero(self):
        assert active_filter_count(DEFAULT_FILTERS) == 0  # badge should not show

    def test_badge_shown_at_one(self):
        f = {**DEFAULT_FILTERS, "addr_mask": "X"}
        assert active_filter_count(f) > 0  # badge visible

    def test_reset_btn_hidden_at_zero(self):
        count = active_filter_count(DEFAULT_FILTERS)
        reset_btn_visible = count > 0
        assert reset_btn_visible is False

    def test_reset_btn_shown_when_filter_active(self):
        f = {**DEFAULT_FILTERS, "tr_type_filter": "15"}
        reset_btn_visible = active_filter_count(f) > 0
        assert reset_btn_visible is True
