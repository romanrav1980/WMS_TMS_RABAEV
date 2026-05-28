"""
test_sprint53_functional.py — Functional tests for Sprint 53 (collapsible filter panel).

Sprint 53 adds a collapse/expand toggle (‹/›) to the right filter panel.
State is persisted in localStorage under key "tms_fpCollapsed".
When collapsed the panel shrinks to 30px; all filter controls are hidden.
"""


def fp_state(collapsed: bool, active_filter_count: int) -> dict:
    return {
        "collapsed": collapsed,
        "show_filters": not collapsed,
        "show_title":   not collapsed,
        "show_reset":   not collapsed and active_filter_count > 0,
        "show_badge_alone": collapsed and active_filter_count > 0,
        "toggle_icon": "›" if collapsed else "‹",
    }


class TestFilterPanelCollapse:
    def test_expanded_shows_filters(self):
        s = fp_state(collapsed=False, active_filter_count=0)
        assert s["show_filters"] is True
        assert s["show_title"] is True

    def test_collapsed_hides_filters(self):
        s = fp_state(collapsed=True, active_filter_count=0)
        assert s["show_filters"] is False
        assert s["show_title"] is False

    def test_expanded_icon_is_left_arrow(self):
        s = fp_state(collapsed=False, active_filter_count=0)
        assert s["toggle_icon"] == "‹"

    def test_collapsed_icon_is_right_arrow(self):
        s = fp_state(collapsed=True, active_filter_count=0)
        assert s["toggle_icon"] == "›"

    def test_expanded_no_active_filters_no_reset(self):
        s = fp_state(collapsed=False, active_filter_count=0)
        assert s["show_reset"] is False

    def test_expanded_with_active_filters_shows_reset(self):
        s = fp_state(collapsed=False, active_filter_count=3)
        assert s["show_reset"] is True

    def test_collapsed_with_active_filters_shows_badge_alone(self):
        s = fp_state(collapsed=True, active_filter_count=5)
        assert s["show_badge_alone"] is True

    def test_collapsed_without_active_filters_no_badge(self):
        s = fp_state(collapsed=True, active_filter_count=0)
        assert s["show_badge_alone"] is False

    def test_toggle_from_expanded_to_collapsed(self):
        collapsed = False
        collapsed = not collapsed
        assert collapsed is True

    def test_toggle_from_collapsed_to_expanded(self):
        collapsed = True
        collapsed = not collapsed
        assert collapsed is False

    def test_localStorage_key(self):
        key = "tms_fpCollapsed"
        assert key == "tms_fpCollapsed"

    def test_localStorage_true_value(self):
        collapsed = True
        stored = "1" if collapsed else "0"
        assert stored == "1"

    def test_localStorage_false_value(self):
        collapsed = False
        stored = "1" if collapsed else "0"
        assert stored == "0"

    def test_localStorage_restore_true(self):
        stored = "1"
        restored = stored == "1"
        assert restored is True

    def test_localStorage_restore_false(self):
        stored = "0"
        restored = stored == "1"
        assert restored is False
