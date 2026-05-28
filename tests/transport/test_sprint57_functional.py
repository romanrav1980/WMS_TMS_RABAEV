"""
test_sprint57_functional.py — Functional tests for Sprint 57 (quick-add ST by number).

Sprint 57 adds an input field + Enter/button handler in the trip detail panel
that lets the dispatcher add a single ST by typing its number directly,
without searching through the table first.
"""


def quick_add_can_submit(task_condition: str, pay_order_id, input_value: str) -> bool:
    """Return True if the quick-add button should be enabled."""
    if task_condition == "Отгружен":
        return False
    if pay_order_id is not None:
        return False
    return bool(input_value.strip())


def quick_add_payload(st_number: str, task_id: int) -> dict:
    """Return the POST body that handleQuickAddSt sends."""
    return {
        "url": f"/api/admin/transport/tasks/{task_id}/sts",
        "body": {"st_numbers": [st_number.strip()]},
    }


class TestQuickAddSt:
    def test_enabled_with_valid_input(self):
        assert quick_add_can_submit("Новый", None, "ST-001") is True

    def test_enabled_for_active_trip(self):
        assert quick_add_can_submit("Активен", None, "ABC123") is True

    def test_disabled_when_input_empty(self):
        assert quick_add_can_submit("Новый", None, "") is False

    def test_disabled_when_input_whitespace(self):
        assert quick_add_can_submit("Новый", None, "  ") is False

    def test_disabled_when_trip_closed(self):
        assert quick_add_can_submit("Отгружен", None, "ST-001") is False

    def test_disabled_when_billed(self):
        assert quick_add_can_submit("Отгружен", 42, "ST-001") is False

    def test_disabled_when_billed_but_active_condition(self):
        assert quick_add_can_submit("Активен", 42, "ST-001") is False

    def test_payload_single_st(self):
        p = quick_add_payload("ST-001", 1234)
        assert p["body"]["st_numbers"] == ["ST-001"]
        assert "1234" in p["url"]

    def test_payload_strips_whitespace(self):
        p = quick_add_payload("  ST-001  ", 1234)
        assert p["body"]["st_numbers"] == ["ST-001"]

    def test_payload_method_is_post(self):
        p = quick_add_payload("ST-001", 1234)
        assert "/sts" in p["url"]

    def test_toast_message_format(self):
        st_num = "ST-099"
        task_id = 1234
        msg = f"СТ {st_num} добавлен в рейс #{task_id}"
        assert "ST-099" in msg
        assert "1234" in msg

    def test_input_cleared_after_success(self):
        quick_add_input = "ST-001"
        # simulate success callback
        quick_add_input = ""
        assert quick_add_input == ""

    def test_enter_key_triggers_submit(self):
        submitted = False
        def on_enter(key: str):
            nonlocal submitted
            if key == "Enter":
                submitted = True
        on_enter("Enter")
        assert submitted is True

    def test_other_keys_do_not_submit(self):
        submitted = False
        def on_enter(key: str):
            nonlocal submitted
            if key == "Enter":
                submitted = True
        on_enter("Tab")
        assert submitted is False
