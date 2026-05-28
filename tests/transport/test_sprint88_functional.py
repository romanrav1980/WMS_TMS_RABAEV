"""Sprint 88: Reschedule trip to next day (→+1 button)."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_handle_reschedule_next_day_exists():
    src = _src()
    assert "async function handleRescheduleNextDay" in src


def test_reschedule_calls_shift_date():
    src = _src()
    idx = src.index("async function handleRescheduleNextDay")
    snippet = src[idx : idx + 400]
    assert "shiftDate" in snippet


def test_reschedule_uses_patch():
    src = _src()
    idx = src.index("async function handleRescheduleNextDay")
    snippet = src[idx : idx + 500]
    assert '"PATCH"' in snippet or "'PATCH'" in snippet


def test_reschedule_shows_confirm():
    src = _src()
    idx = src.index("async function handleRescheduleNextDay")
    snippet = src[idx : idx + 400]
    assert "confirm(" in snippet


def test_reschedule_shows_toast():
    src = _src()
    idx = src.index("async function handleRescheduleNextDay")
    snippet = src[idx : idx + 900]
    assert "showToast" in snippet


def test_reschedule_button_in_tasks_tab():
    src = _src()
    assert "dispatch-reschedule-btn" in src
    assert "handleRescheduleNextDay" in src


def test_reschedule_button_label():
    src = _src()
    assert "→+1" in src


def test_reschedule_not_shown_for_shipped():
    src = _src()
    # Button must be guarded by CONDITION !== "Отгружен"
    idx = src.index("dispatch-reschedule-btn")
    # look back 200 chars for the condition guard
    chunk = src[max(0, idx - 200) : idx + 50]
    assert "Отгружен" in chunk


def test_reschedule_btn_css_exists():
    css = open(
        "admin/wms_admin_frontend/src/styles.css",
        encoding="utf-8",
    ).read()
    assert ".dispatch-reschedule-btn" in css
