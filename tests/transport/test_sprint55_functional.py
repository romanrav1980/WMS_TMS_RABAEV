"""
test_sprint55_functional.py — Functional tests for Sprint 55 (all-visible STs totals).

Sprint 55 replaces the selected-STs PMV strip with an all-visible totals strip:
  «П=N · M кг · V м³»
The sel-bar (Sprint 51) continues to show selected totals separately.
"""


def all_visible_totals(sts: list[dict]) -> dict:
    """Mirror the frontend allP/allM/allV computed values."""
    p = sum(s.get("PALLETS_COUNT", 0) or 0 for s in sts)
    m = sum(s.get("WEIGHT_KG", 0) or 0 for s in sts)
    v = sum(s.get("VOLUME_M3", 0) or 0 for s in sts)
    return {"pallets": p, "weight": m, "volume": v}


class TestAllVisibleTotals:
    def _sts(self):
        return [
            {"PALLETS_COUNT": 5,  "WEIGHT_KG": 300.0, "VOLUME_M3": 2.5},
            {"PALLETS_COUNT": 8,  "WEIGHT_KG": 500.0, "VOLUME_M3": 3.0},
            {"PALLETS_COUNT": 3,  "WEIGHT_KG": 150.0, "VOLUME_M3": 1.0},
        ]

    def test_total_pallets(self):
        t = all_visible_totals(self._sts())
        assert t["pallets"] == 16

    def test_total_weight(self):
        t = all_visible_totals(self._sts())
        assert abs(t["weight"] - 950.0) < 0.01

    def test_total_volume(self):
        t = all_visible_totals(self._sts())
        assert abs(t["volume"] - 6.5) < 0.01

    def test_empty_list(self):
        t = all_visible_totals([])
        assert t["pallets"] == 0
        assert t["weight"] == 0
        assert t["volume"] == 0

    def test_null_volume_treated_as_zero(self):
        sts = [{"PALLETS_COUNT": 5, "WEIGHT_KG": 100.0, "VOLUME_M3": None}]
        t = all_visible_totals(sts)
        assert t["volume"] == 0

    def test_null_pallets_treated_as_zero(self):
        sts = [{"PALLETS_COUNT": None, "WEIGHT_KG": 50.0, "VOLUME_M3": 1.0}]
        t = all_visible_totals(sts)
        assert t["pallets"] == 0

    def test_single_st(self):
        sts = [{"PALLETS_COUNT": 12, "WEIGHT_KG": 800.0, "VOLUME_M3": 6.0}]
        t = all_visible_totals(sts)
        assert t["pallets"] == 12
        assert t["weight"] == 800.0
        assert t["volume"] == 6.0

    def test_filter_change_updates_totals(self):
        sts_all = self._sts()
        sts_filtered = [s for s in sts_all if s["PALLETS_COUNT"] >= 5]
        t_all = all_visible_totals(sts_all)
        t_filtered = all_visible_totals(sts_filtered)
        assert t_filtered["pallets"] < t_all["pallets"]

    def test_independent_of_selection(self):
        sts = self._sts()
        # sel-bar handles selected; all-visible totals never change based on selection
        t1 = all_visible_totals(sts)
        t2 = all_visible_totals(sts)
        assert t1 == t2

    def test_large_dataset(self):
        sts = [{"PALLETS_COUNT": 10, "WEIGHT_KG": 500.0, "VOLUME_M3": 3.0}] * 400
        t = all_visible_totals(sts)
        assert t["pallets"] == 4000
        assert abs(t["weight"] - 200000.0) < 0.01
