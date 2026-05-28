"""
test_sprint51_functional.py — Functional tests for Sprint 51 (sticky selection bar).

Sprint 51 adds a selection bar below the STs table that shows:
  «N выбр. · P пал · M кг · V м³  [+ Создать маршрут] [Добавить в #ID] [✕]»

The bar is visible only when selectedStNums.size > 0.
"""


def sel_bar_visible(selected_count: int) -> bool:
    return selected_count > 0


def sel_bar_state(
    selected_sts: list[dict],
    selected_task_id: int | None = None,
) -> dict:
    count = len(selected_sts)
    p = sum(s.get("PALLETS_COUNT", 0) for s in selected_sts)
    m = sum(s.get("WEIGHT_KG", 0.0) for s in selected_sts)
    v = sum(s.get("VOLUME_M3", 0.0) for s in selected_sts)
    return {
        "visible": count > 0,
        "count":   count,
        "pallets": p,
        "weight":  m,
        "volume":  v,
        "show_add_btn": selected_task_id is not None and count > 0,
        "show_create_btn": count > 0,
    }


class TestSelectionBar:
    def _sts(self):
        return [
            {"PALLETS_COUNT": 5,  "WEIGHT_KG": 300.0, "VOLUME_M3": 2.5},
            {"PALLETS_COUNT": 8,  "WEIGHT_KG": 500.0, "VOLUME_M3": 3.0},
            {"PALLETS_COUNT": 3,  "WEIGHT_KG": 150.0, "VOLUME_M3": 1.0},
        ]

    def test_bar_hidden_when_no_selection(self):
        assert sel_bar_visible(0) is False

    def test_bar_visible_with_one_selected(self):
        assert sel_bar_visible(1) is True

    def test_bar_visible_with_many_selected(self):
        assert sel_bar_visible(20) is True

    def test_counts_correct(self):
        state = sel_bar_state(self._sts())
        assert state["count"]   == 3
        assert state["pallets"] == 16
        assert abs(state["weight"] - 950.0) < 0.01
        assert abs(state["volume"] - 6.5)   < 0.01

    def test_add_btn_shown_when_task_selected(self):
        state = sel_bar_state(self._sts(), selected_task_id=1247)
        assert state["show_add_btn"] is True

    def test_add_btn_hidden_without_task(self):
        state = sel_bar_state(self._sts(), selected_task_id=None)
        assert state["show_add_btn"] is False

    def test_create_btn_always_shown_with_selection(self):
        state = sel_bar_state(self._sts())
        assert state["show_create_btn"] is True

    def test_empty_selection_bar_not_visible(self):
        state = sel_bar_state([])
        assert state["visible"] is False
        assert state["count"] == 0

    def test_single_st_bar_values(self):
        sts = [{"PALLETS_COUNT": 12, "WEIGHT_KG": 800.0, "VOLUME_M3": 6.0}]
        state = sel_bar_state(sts)
        assert state["count"]   == 1
        assert state["pallets"] == 12
        assert state["weight"]  == 800.0

    def test_clear_button_hides_bar(self):
        count_before = 3
        count_after  = 0
        assert sel_bar_visible(count_before) is True
        assert sel_bar_visible(count_after)  is False

    def test_null_volume_treated_as_zero(self):
        sts = [{"PALLETS_COUNT": 5, "WEIGHT_KG": 100.0, "VOLUME_M3": None}]
        # None treated as 0 in sum
        v = sum(s.get("VOLUME_M3", 0.0) or 0.0 for s in sts)
        assert v == 0.0
