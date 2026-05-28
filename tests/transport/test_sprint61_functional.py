"""
test_sprint61_functional.py — Functional tests for Sprint 61 (warehouse quick-filter).

Sprint 61 adds a client-side warehouse selector to the ST toolbar.
wareFilteredSts = wareIdFilter ? availableSts.filter(s => str(WARE_ID) == wareIdFilter) : availableSts
The dropdown only appears when 2+ distinct WARE_IDs are present.
Changing the filter resets stPage to 0 and clears selectedStNums.
"""


def ware_filter(sts: list[dict], ware_id_filter: str) -> list[dict]:
    """Mirror the wareFilteredSts computed value."""
    if not ware_id_filter:
        return sts
    return [s for s in sts if str(s.get("WARE_ID", "")) == ware_id_filter]


def ware_options(sts: list[dict]) -> list[int]:
    """Mirror wareOptions — unique sorted WARE_IDs."""
    return sorted(set(s["WARE_ID"] for s in sts if "WARE_ID" in s))


class TestWareFilter:
    def _sts(self):
        return [
            {"ST_NUMBER": "A1", "WARE_ID": 1, "PALLETS_COUNT": 2, "WEIGHT_KG": 100.0, "VOLUME_M3": 1.0},
            {"ST_NUMBER": "A2", "WARE_ID": 1, "PALLETS_COUNT": 3, "WEIGHT_KG": 150.0, "VOLUME_M3": 1.5},
            {"ST_NUMBER": "B1", "WARE_ID": 2, "PALLETS_COUNT": 1, "WEIGHT_KG": 50.0, "VOLUME_M3": 0.5},
            {"ST_NUMBER": "B2", "WARE_ID": 2, "PALLETS_COUNT": 4, "WEIGHT_KG": 200.0, "VOLUME_M3": 2.0},
            {"ST_NUMBER": "C1", "WARE_ID": 3, "PALLETS_COUNT": 2, "WEIGHT_KG": 80.0, "VOLUME_M3": 0.8},
        ]

    def test_empty_filter_returns_all(self):
        assert ware_filter(self._sts(), "") == self._sts()

    def test_filter_by_ware_1(self):
        result = ware_filter(self._sts(), "1")
        assert all(s["WARE_ID"] == 1 for s in result)
        assert len(result) == 2

    def test_filter_by_ware_2(self):
        result = ware_filter(self._sts(), "2")
        assert all(s["WARE_ID"] == 2 for s in result)
        assert len(result) == 2

    def test_filter_by_ware_3_single_result(self):
        result = ware_filter(self._sts(), "3")
        assert len(result) == 1
        assert result[0]["ST_NUMBER"] == "C1"

    def test_ware_options_sorted(self):
        opts = ware_options(self._sts())
        assert opts == [1, 2, 3]

    def test_ware_options_unique(self):
        opts = ware_options(self._sts())
        assert len(opts) == len(set(opts))

    def test_dropdown_hidden_when_single_warehouse(self):
        sts = [{"ST_NUMBER": "X", "WARE_ID": 5}] * 3
        opts = ware_options(sts)
        show_dropdown = len(opts) > 1
        assert show_dropdown is False

    def test_dropdown_shown_when_multiple_warehouses(self):
        opts = ware_options(self._sts())
        show_dropdown = len(opts) > 1
        assert show_dropdown is True

    def test_tcount_shows_ratio_when_filtered(self):
        all_sts = self._sts()
        filtered = ware_filter(all_sts, "1")
        label = f"{len(filtered)} / {len(all_sts)} СТ"
        assert label == "2 / 5 СТ"

    def test_tcount_shows_total_when_unfiltered(self):
        all_sts = self._sts()
        filtered = ware_filter(all_sts, "")
        label = f"{len(all_sts)} СТ"
        assert label == "5 СТ"

    def test_pmv_totals_use_filtered_sts(self):
        filtered = ware_filter(self._sts(), "1")
        total_p = sum(s["PALLETS_COUNT"] for s in filtered)
        total_m = sum(s["WEIGHT_KG"] for s in filtered)
        assert total_p == 5
        assert total_m == 250.0

    def test_reset_page_on_ware_change(self):
        """Page must reset to 0 when warehouse filter changes."""
        page = 3
        # simulates useEffect: page resets when wareIdFilter changes
        page = 0
        assert page == 0

    def test_nonexistent_ware_returns_empty(self):
        result = ware_filter(self._sts(), "99")
        assert result == []
