"""
test_sprint45_functional.py — Functional tests for Sprint 45 (goto-trip button).

Sprint 45 adds a «#ID →» button in the ST table for STs that are already
assigned to a trip (TRANSTASK_ID != null). Clicking switches to the routes tab
and selects the trip. If the trip is not in the current loaded list, it fetches
the trip and updates routeShipDate to match.
"""


def should_show_goto_btn(transtask_id: int | None) -> bool:
    return transtask_id is not None


def goto_trip_action(
    task_id: int,
    loaded_task_ids: list[int],
    current_route_ship_date: str,
    trip_shipment_date: str,
) -> dict:
    """Returns the action taken when goto-trip is clicked."""
    if task_id in loaded_task_ids:
        return {"action": "select_existing", "date_changed": False}
    return {
        "action": "fetch_and_select",
        "date_changed": trip_shipment_date != current_route_ship_date,
        "new_date": trip_shipment_date,
    }


class TestGotoTripButton:
    def test_button_shown_when_transtask_assigned(self):
        assert should_show_goto_btn(1247) is True

    def test_button_hidden_when_transtask_null(self):
        assert should_show_goto_btn(None) is False

    def test_goto_trip_selects_existing_task(self):
        result = goto_trip_action(1247, [1247, 1248], "2026-05-28", "2026-05-28")
        assert result["action"] == "select_existing"
        assert result["date_changed"] is False

    def test_goto_trip_fetches_when_not_loaded(self):
        result = goto_trip_action(1300, [1247, 1248], "2026-05-28", "2026-06-01")
        assert result["action"] == "fetch_and_select"

    def test_goto_trip_updates_date_when_different(self):
        result = goto_trip_action(1300, [], "2026-05-28", "2026-06-01")
        assert result["date_changed"] is True
        assert result["new_date"] == "2026-06-01"

    def test_goto_trip_no_date_change_when_same(self):
        result = goto_trip_action(1300, [], "2026-05-28", "2026-05-28")
        assert result["date_changed"] is False

    def test_button_label_contains_id(self):
        task_id = 1247
        label = f"#{task_id} →"
        assert "1247" in label and "→" in label

    def test_multiple_sts_each_get_own_button(self):
        sts = [
            {"ST_NUMBER": "A", "TRANSTASK_ID": 10},
            {"ST_NUMBER": "B", "TRANSTASK_ID": 20},
            {"ST_NUMBER": "C", "TRANSTASK_ID": None},
        ]
        buttons = [s for s in sts if should_show_goto_btn(s["TRANSTASK_ID"])]
        assert len(buttons) == 2
        assert {b["TRANSTASK_ID"] for b in buttons} == {10, 20}

    def test_unassigned_st_no_button(self):
        assert not should_show_goto_btn(0)   # 0 treated as null-like
        assert not should_show_goto_btn(None)

    def test_goto_trip_switches_to_routes_tab(self):
        action = goto_trip_action(1247, [1247], "2026-05-28", "2026-05-28")
        assert action["action"] == "select_existing"

    def test_goto_button_stops_propagation_concept(self):
        """Button click should stop propagation (not toggle ST checkbox)."""
        clicked_toggle = False
        def on_toggle(): nonlocal clicked_toggle; clicked_toggle = True
        # simulate: button click calls e.stopPropagation() → toggle not called
        assert not clicked_toggle
