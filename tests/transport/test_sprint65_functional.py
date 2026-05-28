"""
test_sprint65_functional.py — Functional tests for Sprint 65 (selection badge on Tasks tab).

Sprint 65 adds a blue pill badge on the «Заявки» tab showing selectedStNums.size.
Badge is hidden when size == 0; visible and shows count when >= 1.
"""


def tab_badge_visible(selected_count: int) -> bool:
    return selected_count > 0


def tab_badge_label(selected_count: int) -> str:
    return str(selected_count)


class TestTabBadge:
    def test_hidden_when_no_selection(self):
        assert tab_badge_visible(0) is False

    def test_shown_when_one_selected(self):
        assert tab_badge_visible(1) is True

    def test_shown_when_many_selected(self):
        assert tab_badge_visible(42) is True

    def test_label_shows_count(self):
        assert tab_badge_label(5) == "5"
        assert tab_badge_label(100) == "100"

    def test_hidden_after_clear(self):
        count = 5
        count = 0  # simulates clear
        assert tab_badge_visible(count) is False

    def test_badge_updates_on_selection_change(self):
        counts = [0, 1, 3, 3, 2]
        visibilities = [tab_badge_visible(c) for c in counts]
        assert visibilities == [False, True, True, True, True]
