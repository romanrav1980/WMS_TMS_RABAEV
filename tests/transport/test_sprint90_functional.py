"""Sprint 90: Click-to-copy ST number to clipboard in trip detail rows."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_task_st_row_has_st_copied_state():
    src = _src()
    idx = src.index("function TaskStTableRow")
    snippet = src[idx : idx + 600]
    assert "stCopied" in snippet


def test_route_task_st_row_has_st_copied_state():
    src = _src()
    idx = src.index("function RouteTaskStRow")
    snippet = src[idx : idx + 600]
    assert "stCopied" in snippet


def test_copy_fn_uses_clipboard_api():
    src = _src()
    assert "navigator.clipboard.writeText" in src


def test_copy_fn_uses_st_number():
    src = _src()
    idx = src.index("function copyStNum")
    snippet = src[idx : idx + 200]
    assert "ST_NUMBER" in snippet


def test_st_copy_cell_class_present():
    src = _src()
    assert "dispatch-st-copy-cell" in src


def test_st_copied_indicator_markup():
    src = _src()
    assert "dispatch-st-copied" in src


def test_copied_shows_checkmark():
    src = _src()
    idx = src.index("dispatch-st-copied")
    snippet = src[idx : idx + 50]
    assert "✓" in snippet


def test_copy_timeout_clears_state():
    src = _src()
    idx = src.index("function copyStNum")
    snippet = src[idx : idx + 300]
    assert "setTimeout" in snippet
    assert "setStCopied(false)" in snippet


def test_copy_present_in_both_components():
    src = _src()
    count = src.count("dispatch-st-copy-cell")
    assert count >= 2, f"Expected in both TaskStTableRow and RouteTaskStRow, found {count}"


def test_css_copy_cell_exists():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-st-copy-cell" in css
    assert ".dispatch-st-copied" in css
    assert "st-copy-fade" in css
