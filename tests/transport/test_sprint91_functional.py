"""
test_sprint91_functional.py — Sprint 91: Sort trip STs by time window.

Feature: «⏱ Окна» button in trip detail STs toolbar sorts rows by TIME_FROM (nulls last).
Pure frontend sort — no new backend endpoints.
"""

import ast
import pathlib

SRC = pathlib.Path(
    "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx"
).read_text(encoding="utf-8")
CSS = pathlib.Path("admin/wms_admin_frontend/src/styles.css").read_text(encoding="utf-8")


def _snip(marker: str, chars: int = 800) -> str:
    idx = SRC.index(marker)
    return SRC[idx: idx + chars]


# ---------------------------------------------------------------------------
# State variable
# ---------------------------------------------------------------------------

def test_trip_st_sort_by_time_state_declared():
    """tripStSortByTime state variable exists."""
    assert "tripStSortByTime" in SRC
    assert "setTripStSortByTime" in SRC


def test_trip_st_sort_by_time_initial_false():
    """Default value is false."""
    snip = _snip("tripStSortByTime", 120)
    assert "useState(false)" in snip


# ---------------------------------------------------------------------------
# Reset on task switch
# ---------------------------------------------------------------------------

def test_trip_st_sort_reset_on_task_switch():
    """setTripStSortByTime(false) is called when selectTask runs."""
    assert "setTripStSortByTime(false)" in SRC


# ---------------------------------------------------------------------------
# filteredTaskSts logic
# ---------------------------------------------------------------------------

def test_filtered_task_sts_has_sort_block():
    """filteredTaskSts sorts by TIME_FROM when tripStSortByTime is true."""
    snip = _snip("if (tripStSortByTime)", 400)
    assert "TIME_FROM" in snip


def test_sort_uses_fmt_time():
    """Sort comparator calls fmtTime for time extraction."""
    snip = _snip("if (tripStSortByTime)", 400)
    assert "fmtTime" in snip


def test_sort_nulls_last():
    """STs without TIME_FROM sort to the end (99:99 fallback)."""
    snip = _snip("if (tripStSortByTime)", 400)
    assert "99:99" in snip


def test_sort_uses_locale_compare():
    """String comparison used for HH:MM ordering."""
    snip = _snip("if (tripStSortByTime)", 400)
    assert "localeCompare" in snip


# ---------------------------------------------------------------------------
# Toolbar button
# ---------------------------------------------------------------------------

def test_toolbar_has_timesort_button():
    """Toolbar contains the ⏱ Окна sort button."""
    assert "dispatch-trip-timesort-btn" in SRC


def test_timesort_button_only_when_time_data():
    """Sort button is only rendered when at least one ST has TIME_FROM."""
    snip = _snip("Sprint 91 — sort by time window", 300)
    assert "TIME_FROM" in snip


def test_timesort_button_active_class():
    """Active CSS class applied when sort is on."""
    snip = _snip("dispatch-trip-timesort-btn", 200)
    assert 'active' in snip


def test_timesort_button_toggle():
    """Clicking the button toggles tripStSortByTime."""
    snip = _snip("dispatch-trip-timesort-btn", 300)
    assert "setTripStSortByTime" in snip


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def test_css_timesort_btn_defined():
    """CSS rule for .dispatch-trip-timesort-btn exists."""
    assert ".dispatch-trip-timesort-btn" in CSS


def test_css_timesort_btn_active_state():
    """Active state CSS rule exists."""
    assert ".dispatch-trip-timesort-btn.active" in CSS
