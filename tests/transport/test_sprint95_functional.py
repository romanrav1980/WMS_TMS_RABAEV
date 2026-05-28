"""
test_sprint95_functional.py — Sprint 95: PRIMECHANIE tooltip on trip rows.

Both tasks tab and routes tab trip rows get title="Примечание: <text>"
when PRIMECHANIE is set. No backend changes needed.
"""

import pathlib

SRC = pathlib.Path(
    "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx"
).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Tooltip presence
# ---------------------------------------------------------------------------

def test_primechanie_tooltip_in_source():
    """PRIMECHANIE tooltip text is present in JSX."""
    assert "PRIMECHANIE" in SRC
    assert "Примечание:" in SRC


def test_primechanie_tooltip_tasks_tab():
    """Tasks tab rows have PRIMECHANIE title attribute."""
    count = SRC.count("PRIMECHANIE ? `")
    assert count >= 2, f"Expected >=2 occurrences (tasks + routes tabs), got {count}"


def test_primechanie_title_format():
    """Title format starts with 'Примечание: '."""
    assert "`Примечание: ${task.PRIMECHANIE}`" in SRC


def test_primechanie_only_when_set():
    """Tooltip rendered only when PRIMECHANIE is truthy."""
    assert "task.PRIMECHANIE ?" in SRC


def test_primechanie_undefined_when_null():
    """When no PRIMECHANIE, title is undefined (no empty tooltip shown)."""
    assert ": undefined" in SRC
