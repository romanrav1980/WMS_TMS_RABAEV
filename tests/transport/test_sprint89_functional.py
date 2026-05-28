"""Sprint 89: Unready-only filter toggle in trip detail STs toolbar."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_trip_st_unready_only_state_exists():
    src = _src()
    assert "tripStUnreadyOnly" in src


def test_unready_only_initial_false():
    src = _src()
    assert 'useState(false)' in src
    idx = src.index("tripStUnreadyOnly")
    snippet = src[idx : idx + 100]
    assert "useState(false)" in snippet


def test_filtered_task_sts_applies_unready_filter():
    src = _src()
    idx = src.index("Sprint 72 — filter within trip detail STs")
    snippet = src[idx : idx + 700]
    assert "tripStUnreadyOnly" in snippet
    assert "VERIFY_PERC < 100" in snippet


def test_filtered_task_sts_checks_not_null():
    src = _src()
    idx = src.index("Sprint 72 — filter within trip detail STs")
    snippet = src[idx : idx + 700]
    assert "VERIFY_PERC !== null" in snippet


def test_unready_toggle_reset_on_task_switch():
    src = _src()
    idx = src.index("setTripStUnreadyOnly(false)")
    assert idx > 0


def test_unready_button_in_toolbar():
    src = _src()
    assert "dispatch-trip-unready-btn" in src


def test_unready_button_label():
    src = _src()
    assert "Несобр." in src


def test_unready_button_conditional_render():
    src = _src()
    idx = src.index("dispatch-trip-unready-btn")
    chunk = src[max(0, idx - 200) : idx + 50]
    assert "VERIFY_PERC !== null" in chunk


def test_unready_button_active_class():
    src = _src()
    idx = src.index("dispatch-trip-unready-btn")
    snippet = src[idx : idx + 200]
    assert "active" in snippet


def test_count_shows_filtered_when_unready_active():
    src = _src()
    idx = src.index("dispatch-trip-sts-count")
    snippet = src[idx : idx + 200]
    assert "tripStUnreadyOnly" in snippet


def test_css_unready_btn_exists():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-trip-unready-btn" in css
    assert ".dispatch-trip-unready-btn.active" in css
