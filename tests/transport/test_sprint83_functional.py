"""Sprint 83: Amber left-border for unready available STs."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def _css():
    return open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()


def test_avail_unready_class_applied():
    src = _src()
    assert "dispatch-avail-unready" in src, "dispatch-avail-unready class missing in TSX"


def test_avail_unready_condition():
    src = _src()
    idx = src.index("dispatch-avail-unready")
    snippet = src[max(0, idx - 200) : idx + 100]
    assert "VERIFY_PERC !== null" in snippet
    assert "VERIFY_PERC < 100" in snippet


def test_avail_unready_only_when_not_checked():
    src = _src()
    idx = src.index("dispatch-avail-unready")
    snippet = src[max(0, idx - 200) : idx + 100]
    assert "!checked" in snippet, "Class should only apply when row is not checked"


def test_avail_unready_css_defined():
    css = _css()
    assert ".dispatch-avail-unready" in css


def test_st_ready_still_present():
    src = _src()
    assert "dispatch-st-ready" in src, "Sprint 50 class should still be present"
    css = _css()
    assert ".dispatch-st-ready" in css
