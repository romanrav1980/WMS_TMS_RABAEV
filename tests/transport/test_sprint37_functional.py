"""
test_sprint37_functional.py — Functional tests for Sprint 37.

Sprint 37 adds two UX features to TransportDispatchPage:
  1. «Выделить все» header checkbox in flat-mode available-ST table
  2. Auto-refresh: every 60 s the data reloads automatically (unless
     a dialog/edit is open)

Test scope — frontend state logic simulated in Python (no React runtime):
  - Select-all: selects every visible ST
  - Select-all when all selected: deselects all (toggle behaviour)
  - Partial selection → select-all → all selected
  - Auto-refresh: disabled flag prevents periodic reload
  - Auto-refresh: skipped when loading/editing/dialog open
  - Auto-refresh: timestamp updated after each tick

Backend is unchanged for this sprint — no new endpoints.
"""

from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers / fakes
# ---------------------------------------------------------------------------

def make_st(st_number: str) -> dict:
    return {"ST_NUMBER": st_number, "PALLETS_COUNT": 2, "WEIGHT_KG": 100.0}


# ---------------------------------------------------------------------------
# Select-all logic simulation
# ---------------------------------------------------------------------------

class SelectAllSimulator:
    def __init__(self, sts: list[dict]):
        self.available_sts = sts
        self.selected_st_nums: set[str] = set()

    @property
    def all_selected(self) -> bool:
        return (
            len(self.available_sts) > 0
            and all(s["ST_NUMBER"] in self.selected_st_nums for s in self.available_sts)
        )

    def toggle_select_all(self):
        if self.all_selected:
            self.selected_st_nums = set()
        else:
            self.selected_st_nums = {s["ST_NUMBER"] for s in self.available_sts}


class TestSelectAll:
    def _sim(self, n: int) -> SelectAllSimulator:
        return SelectAllSimulator([make_st(f"ST-{i:03d}") for i in range(1, n + 1)])

    def test_empty_list_all_selected_is_false(self):
        sim = SelectAllSimulator([])
        assert sim.all_selected is False

    def test_select_all_selects_every_st(self):
        sim = self._sim(5)
        sim.toggle_select_all()
        assert len(sim.selected_st_nums) == 5
        assert all(f"ST-{i:03d}" in sim.selected_st_nums for i in range(1, 6))

    def test_select_all_when_all_already_selected_deselects_all(self):
        sim = self._sim(5)
        sim.toggle_select_all()  # select all
        sim.toggle_select_all()  # deselect all
        assert len(sim.selected_st_nums) == 0

    def test_partial_selection_then_select_all(self):
        sim = self._sim(5)
        sim.selected_st_nums = {"ST-001", "ST-002"}
        sim.toggle_select_all()
        assert len(sim.selected_st_nums) == 5

    def test_all_selected_property_after_select_all(self):
        sim = self._sim(3)
        assert sim.all_selected is False
        sim.toggle_select_all()
        assert sim.all_selected is True

    def test_all_selected_false_when_one_missing(self):
        sim = self._sim(3)
        sim.selected_st_nums = {"ST-001", "ST-002"}  # missing ST-003
        assert sim.all_selected is False

    def test_select_all_works_with_one_st(self):
        sim = self._sim(1)
        sim.toggle_select_all()
        assert sim.selected_st_nums == {"ST-001"}

    def test_toggle_twice_returns_to_empty(self):
        sim = self._sim(10)
        sim.toggle_select_all()
        sim.toggle_select_all()
        assert sim.selected_st_nums == set()


# ---------------------------------------------------------------------------
# Auto-refresh logic simulation
# ---------------------------------------------------------------------------

class AutoRefreshSimulator:
    def __init__(self, enabled: bool = True):
        self.auto_refresh = enabled
        self.refresh_count = 0
        self.last_refresh_at: str = ""
        self.loading = False
        self.create_dialog = False
        self.edit_mode = False
        self.cluster_create_raion = None
        self.billing_dialog = False

    def _is_blocked(self) -> bool:
        return (
            self.loading
            or self.create_dialog
            or self.edit_mode
            or self.cluster_create_raion is not None
            or self.billing_dialog
        )

    def tick(self):
        if not self.auto_refresh:
            return
        if self._is_blocked():
            return
        self.refresh_count += 1
        self.last_refresh_at = datetime.now().strftime("%H:%M")


class TestAutoRefresh:
    def test_tick_increments_refresh_count(self):
        sim = AutoRefreshSimulator(enabled=True)
        sim.tick()
        assert sim.refresh_count == 1

    def test_tick_when_disabled_does_nothing(self):
        sim = AutoRefreshSimulator(enabled=False)
        sim.tick()
        assert sim.refresh_count == 0

    def test_tick_sets_last_refresh_at(self):
        sim = AutoRefreshSimulator(enabled=True)
        assert sim.last_refresh_at == ""
        sim.tick()
        assert sim.last_refresh_at != ""

    def test_tick_blocked_during_loading(self):
        sim = AutoRefreshSimulator(enabled=True)
        sim.loading = True
        sim.tick()
        assert sim.refresh_count == 0

    def test_tick_blocked_during_create_dialog(self):
        sim = AutoRefreshSimulator(enabled=True)
        sim.create_dialog = True
        sim.tick()
        assert sim.refresh_count == 0

    def test_tick_blocked_during_edit_mode(self):
        sim = AutoRefreshSimulator(enabled=True)
        sim.edit_mode = True
        sim.tick()
        assert sim.refresh_count == 0

    def test_tick_blocked_when_cluster_dialog_open(self):
        sim = AutoRefreshSimulator(enabled=True)
        sim.cluster_create_raion = "Север"
        sim.tick()
        assert sim.refresh_count == 0

    def test_tick_blocked_during_billing_dialog(self):
        sim = AutoRefreshSimulator(enabled=True)
        sim.billing_dialog = True
        sim.tick()
        assert sim.refresh_count == 0

    def test_multiple_ticks_accumulate(self):
        sim = AutoRefreshSimulator(enabled=True)
        for _ in range(5):
            sim.tick()
        assert sim.refresh_count == 5

    def test_enable_after_disable_resumes(self):
        sim = AutoRefreshSimulator(enabled=False)
        sim.tick()
        assert sim.refresh_count == 0
        sim.auto_refresh = True
        sim.tick()
        assert sim.refresh_count == 1
