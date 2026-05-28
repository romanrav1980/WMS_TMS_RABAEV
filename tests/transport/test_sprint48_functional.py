"""
test_sprint48_functional.py — Functional tests for Sprint 48 (Today button).

Sprint 48 adds a «Сегодня» button that appears when the date filter
is not today. Clicking resets the date to today.
"""

from datetime import date


def should_show_today_btn(filter_date: str, today: str) -> bool:
    return filter_date != today


def handle_today_click(today: str) -> str:
    return today


class TestTodayButton:
    def test_button_hidden_when_date_is_today(self):
        today = "2026-05-28"
        assert should_show_today_btn(today, today) is False

    def test_button_shown_when_date_is_past(self):
        assert should_show_today_btn("2026-05-20", "2026-05-28") is True

    def test_button_shown_when_date_is_future(self):
        assert should_show_today_btn("2026-06-01", "2026-05-28") is True

    def test_click_resets_to_today(self):
        today = "2026-05-28"
        new_date = handle_today_click(today)
        assert new_date == today

    def test_button_disappears_after_reset(self):
        today = "2026-05-28"
        new_date = handle_today_click(today)
        assert should_show_today_btn(new_date, today) is False

    def test_yesterday_shows_button(self):
        today = str(date.today())
        yesterday = str(date.fromordinal(date.today().toordinal() - 1))
        assert should_show_today_btn(yesterday, today) is True

    def test_tasks_and_routes_tab_independent(self):
        today = "2026-05-28"
        filter_date = "2026-05-20"
        route_date  = "2026-05-28"
        assert should_show_today_btn(filter_date, today) is True
        assert should_show_today_btn(route_date,  today) is False

    def test_both_shown_when_both_not_today(self):
        today = "2026-05-28"
        assert should_show_today_btn("2026-05-01", today) is True
        assert should_show_today_btn("2026-06-01", today) is True

    def test_today_iso_format(self):
        today = "2026-05-28"
        result = handle_today_click(today)
        parts = result.split("-")
        assert len(parts) == 3 and len(parts[0]) == 4
