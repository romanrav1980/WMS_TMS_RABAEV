"""Sprint 87: Enhanced close-trip confirmation with unready ST warning."""


def _src():
    return open(
        "admin/wms_admin_frontend/src/components/TransportDispatchPage.tsx",
        encoding="utf-8",
    ).read()


def test_handle_close_has_unready_check():
    src = _src()
    idx = src.index("async function handleClose")
    snippet = src[idx : idx + 500]
    assert "unreadyCount" in snippet, "unreadyCount variable missing"
    assert "VERIFY_PERC < 100" in snippet


def test_warning_message_shows_count():
    src = _src()
    idx = src.index("async function handleClose")
    snippet = src[idx : idx + 500]
    assert "unreadyCount > 0" in snippet


def test_confirm_uses_conditional_message():
    src = _src()
    idx = src.index("async function handleClose")
    snippet = src[idx : idx + 500]
    assert "confirmMsg" in snippet
    assert "confirm(confirmMsg)" in snippet


def test_original_confirm_text_retained():
    src = _src()
    idx = src.index("async function handleClose")
    snippet = src[idx : idx + 500]
    assert "отгруженный" in snippet
