"""
test_sprint92_functional.py — Sprint 92: Copy all ST numbers to clipboard.

Button «📋 СТ» in trip detail toolbar copies filteredTaskSts ST numbers
(one per line) to clipboard; shows «✓ Скопировано» feedback for 1.8 s.
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
# State variable
# ---------------------------------------------------------------------------

def test_trip_sts_copied_state_declared():
    """tripStsCopied state variable exists."""
    assert "tripStsCopied" in SRC
    assert "setTripStsCopied" in SRC


def test_trip_sts_copied_initial_false():
    """Default value is false."""
    snip = _snip("tripStsCopied", 120)
    assert "useState(false)" in snip


# ---------------------------------------------------------------------------
# Reset on task switch
# ---------------------------------------------------------------------------

def test_trip_sts_copied_reset_on_task_switch():
    """setTripStsCopied(false) called on task switch."""
    assert "setTripStsCopied(false)" in SRC


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------

def test_copy_sts_button_exists():
    """Copy STs button element present in JSX."""
    assert "dispatch-trip-copy-sts-btn" in SRC


def test_copy_sts_button_uses_filtered_list():
    """Button copies filteredTaskSts (respects active filters)."""
    snip = _snip("dispatch-trip-copy-sts-btn", 600)
    assert "filteredTaskSts" in snip


def test_copy_sts_button_newline_separator():
    """ST numbers joined with newline."""
    snip = _snip("dispatch-trip-copy-sts-btn", 600)
    assert "\\n" in snip or '"\\n"' in snip or "join" in snip


def test_copy_sts_uses_clipboard_api():
    """Uses navigator.clipboard.writeText."""
    snip = _snip("dispatch-trip-copy-sts-btn", 600)
    assert "clipboard.writeText" in snip


def test_copy_sts_feedback_label():
    """Button shows confirmation text after copy."""
    snip = _snip("dispatch-trip-copy-sts-btn", 600)
    assert "Скопировано" in snip or "copied" in snip.lower()


def test_copy_sts_copied_class_applied():
    """Active class «copied» applied to button when tripStsCopied is true."""
    snip = _snip("dispatch-trip-copy-sts-btn", 300)
    assert "copied" in snip


def test_copy_sts_auto_reset():
    """Feedback auto-resets via setTimeout."""
    snip = _snip("dispatch-trip-copy-sts-btn", 600)
    assert "setTimeout" in snip


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def test_css_copy_sts_btn_defined():
    """CSS rule for .dispatch-trip-copy-sts-btn exists."""
    assert ".dispatch-trip-copy-sts-btn" in CSS


def test_css_copy_sts_btn_copied_state():
    """CSS .copied variant for green confirmation feedback."""
    assert ".dispatch-trip-copy-sts-btn.copied" in CSS
