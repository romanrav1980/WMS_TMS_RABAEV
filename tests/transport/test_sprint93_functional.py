"""
test_sprint93_functional.py — Sprint 93: Empty trips warning in day summary.

dayEmptyTasks counts active trips with 0 pallets; «⚠ N пустых» shown in
day summary bar when > 0. No backend changes.
"""

import pathlib

SRC = pathlib.Path(
    "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx"
).read_text(encoding="utf-8")
CSS = pathlib.Path("admin/wms_admin_frontend/src/styles.css").read_text(encoding="utf-8")


def _snip(marker: str, chars: int = 500) -> str:
    idx = SRC.index(marker)
    return SRC[idx: idx + chars]


# ---------------------------------------------------------------------------
# Derived value
# ---------------------------------------------------------------------------

def test_day_empty_tasks_declared():
    """dayEmptyTasks derived constant exists."""
    assert "dayEmptyTasks" in SRC


def test_day_empty_tasks_excludes_closed():
    """Closed (Отгружен) trips not counted as empty."""
    snip = _snip("dayEmptyTasks", 300)
    assert "Отгружен" in snip


def test_day_empty_tasks_excludes_cancelled():
    """Cancelled (Отменён) trips not counted as empty."""
    snip = _snip("dayEmptyTasks", 300)
    assert "Отменён" in snip


def test_day_empty_tasks_checks_pallet_count():
    """Filter uses PALLET_COUNT field."""
    snip = _snip("dayEmptyTasks", 300)
    assert "PALLET_COUNT" in snip


# ---------------------------------------------------------------------------
# JSX badge
# ---------------------------------------------------------------------------

def test_empty_warn_badge_shown_conditionally():
    """Warning badge shown only when dayEmptyTasks > 0."""
    assert "dayEmptyTasks > 0" in SRC


def test_empty_warn_badge_css_class():
    """Badge uses dispatch-ds-empty-warn CSS class."""
    assert "dispatch-ds-empty-warn" in SRC


def test_empty_warn_badge_text():
    """Badge shows «пустых» label."""
    snip = _snip("dispatch-ds-empty-warn", 200)
    assert "пустых" in snip


def test_empty_warn_badge_icon():
    """Badge includes warning icon."""
    snip = _snip("dispatch-ds-empty-warn", 200)
    assert "⚠" in snip


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def test_css_empty_warn_defined():
    """CSS rule for .dispatch-ds-empty-warn exists."""
    assert ".dispatch-ds-empty-warn" in CSS


def test_css_empty_warn_amber_color():
    """Warning uses amber/orange color."""
    snip = CSS[CSS.index(".dispatch-ds-empty-warn"): CSS.index(".dispatch-ds-empty-warn") + 100]
    assert "#b45309" in snip or "orange" in snip or "amber" in snip
