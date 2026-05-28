"""
test_sprint44_functional.py — Functional tests for Sprint 44 (Escape key handler).

Sprint 44 adds a global Escape key handler with priority chain:
  1. Close create-dialog
  2. Close cluster-create dialog
  3. Cancel edit mode
  4. Deselect available STs
  5. Deselect trip STs

Priority is first-match: only one action fires per Escape press.
"""


def escape_action(
    create_dialog: bool = False,
    cluster_create_raion: str | None = None,
    edit_mode: bool = False,
    selected_st_nums: set | None = None,
    selected_trip_st_nums: set | None = None,
) -> str:
    """Returns the action taken, or 'none' if nothing to do."""
    selected_st_nums = selected_st_nums or set()
    selected_trip_st_nums = selected_trip_st_nums or set()

    if create_dialog:          return "close_create_dialog"
    if cluster_create_raion:   return "close_cluster_dialog"
    if edit_mode:              return "cancel_edit"
    if selected_st_nums:       return "deselect_sts"
    if selected_trip_st_nums:  return "deselect_trip_sts"
    return "none"


class TestEscapeHandler:
    def test_create_dialog_takes_priority(self):
        action = escape_action(
            create_dialog=True, edit_mode=True,
            selected_st_nums={"ST001"}
        )
        assert action == "close_create_dialog"

    def test_cluster_dialog_second_priority(self):
        action = escape_action(
            cluster_create_raion="Лысьва",
            edit_mode=True,
            selected_st_nums={"ST001"},
        )
        assert action == "close_cluster_dialog"

    def test_edit_mode_third(self):
        action = escape_action(edit_mode=True, selected_st_nums={"ST001"})
        assert action == "cancel_edit"

    def test_deselect_sts_fourth(self):
        action = escape_action(selected_st_nums={"ST001", "ST002"})
        assert action == "deselect_sts"

    def test_deselect_trip_sts_fifth(self):
        action = escape_action(selected_trip_st_nums={"ST003"})
        assert action == "deselect_trip_sts"

    def test_nothing_to_do(self):
        action = escape_action()
        assert action == "none"

    def test_only_edit_mode(self):
        assert escape_action(edit_mode=True) == "cancel_edit"

    def test_only_cluster_dialog(self):
        assert escape_action(cluster_create_raion="Пермь") == "close_cluster_dialog"

    def test_create_dialog_blocks_deselect(self):
        action = escape_action(create_dialog=True, selected_st_nums={"ST001", "ST002", "ST003"})
        assert action == "close_create_dialog"

    def test_empty_selections_treated_as_none(self):
        action = escape_action(selected_st_nums=set(), selected_trip_st_nums=set())
        assert action == "none"

    def test_single_st_deselects(self):
        assert escape_action(selected_st_nums={"ONLY_ONE"}) == "deselect_sts"

    def test_trip_sts_only_when_no_sts(self):
        action = escape_action(
            selected_st_nums=set(),
            selected_trip_st_nums={"T1", "T2"},
        )
        assert action == "deselect_trip_sts"
