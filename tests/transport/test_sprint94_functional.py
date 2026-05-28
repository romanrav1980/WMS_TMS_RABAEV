"""
test_sprint94_functional.py — Sprint 94: Amber left-border for trips with unready STs.

Trips in tasks tab and routes tab get class dispatch-trip-unready when:
  READY_PERC > 0 AND < 100 AND condition not Отгружен/Отменён.
No backend changes needed (READY_PERC already in task list response).
"""

import pathlib

SRC = pathlib.Path(
    "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx"
).read_text(encoding="utf-8")
CSS = pathlib.Path("admin/wms_admin_frontend/src/styles.css").read_text(encoding="utf-8")


def _snip(marker: str, chars: int = 600) -> str:
    idx = SRC.index(marker)
    return SRC[idx: idx + chars]


# ---------------------------------------------------------------------------
# CSS class application — tasks tab
# ---------------------------------------------------------------------------

def test_tasks_tab_unready_class_applied():
    """dispatch-trip-unready class used in tasks tab rows."""
    assert "dispatch-trip-unready" in SRC


def test_tasks_tab_checks_ready_perc_range():
    """READY_PERC > 0 AND < 100 condition in tasks tab."""
    snip = _snip("Sprint 94", 300)
    assert "READY_PERC" in snip
    assert "< 100" in snip
    assert "> 0" in snip


def test_tasks_tab_excludes_closed():
    """Closed (Отгружен) trips not marked unready."""
    snip = _snip("Sprint 94", 300)
    assert "Отгружен" in snip


def test_tasks_tab_excludes_cancelled():
    """Cancelled (Отменён) trips not marked unready."""
    snip = _snip("Sprint 94", 300)
    assert "Отменён" in snip


# ---------------------------------------------------------------------------
# CSS class application — routes tab (second occurrence)
# ---------------------------------------------------------------------------

def test_routes_tab_unready_class_applied():
    """dispatch-trip-unready class used in routes tab rows too."""
    count = SRC.count("dispatch-trip-unready")
    assert count >= 2, f"Expected at least 2 occurrences, got {count}"


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def test_css_trip_unready_class_defined():
    """CSS rule .dispatch-trip-unready exists."""
    assert ".dispatch-trip-unready" in CSS


def test_css_trip_unready_amber_border():
    """Left border uses amber color (#f59e0b)."""
    snip = CSS[CSS.index(".dispatch-trip-unready"): CSS.index(".dispatch-trip-unready") + 100]
    assert "#f59e0b" in snip


def test_css_trip_unready_is_important():
    """Border uses !important to override selected-row styling."""
    snip = CSS[CSS.index(".dispatch-trip-unready"): CSS.index(".dispatch-trip-unready") + 100]
    assert "!important" in snip
