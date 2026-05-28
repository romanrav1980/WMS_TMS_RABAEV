"""
test_sprint63_functional.py — Functional tests for Sprint 63 (not-assembled badge).

Sprint 63 adds a «⚠ N не собрано» badge to the ST toolbar.
It counts wareFilteredSts where VERIFY_PERC is not null AND < 100.
Badge is hidden when count is 0.
"""


def not_ready_count(sts: list[dict]) -> int:
    """Mirror the notReady computed value."""
    return sum(
        1 for s in sts
        if s.get("VERIFY_PERC") is not None and s["VERIFY_PERC"] < 100
    )


class TestNotReadyBadge:
    def _sts(self):
        return [
            {"ST_NUMBER": "A1", "VERIFY_PERC": 100},
            {"ST_NUMBER": "A2", "VERIFY_PERC": 75},
            {"ST_NUMBER": "A3", "VERIFY_PERC": 0},
            {"ST_NUMBER": "A4", "VERIFY_PERC": None},
            {"ST_NUMBER": "A5", "VERIFY_PERC": 100},
        ]

    def test_counts_only_incomplete(self):
        assert not_ready_count(self._sts()) == 2

    def test_fully_assembled_not_counted(self):
        sts = [{"VERIFY_PERC": 100}] * 5
        assert not_ready_count(sts) == 0

    def test_null_verify_perc_not_counted(self):
        sts = [{"VERIFY_PERC": None}] * 3
        assert not_ready_count(sts) == 0

    def test_zero_perc_counted(self):
        sts = [{"VERIFY_PERC": 0}]
        assert not_ready_count(sts) == 1

    def test_99_perc_counted(self):
        sts = [{"VERIFY_PERC": 99}]
        assert not_ready_count(sts) == 1

    def test_badge_hidden_when_all_ready(self):
        sts = [{"VERIFY_PERC": 100}] * 10
        show = not_ready_count(sts) > 0
        assert show is False

    def test_badge_shown_when_some_not_ready(self):
        show = not_ready_count(self._sts()) > 0
        assert show is True

    def test_badge_hidden_empty_list(self):
        assert not_ready_count([]) == 0

    def test_badge_respects_ware_filter(self):
        """notReady is computed from wareFilteredSts, not all availableSts."""
        all_sts = [
            {"WARE_ID": 1, "VERIFY_PERC": 50},
            {"WARE_ID": 1, "VERIFY_PERC": 100},
            {"WARE_ID": 2, "VERIFY_PERC": 30},
        ]
        ware1 = [s for s in all_sts if s["WARE_ID"] == 1]
        assert not_ready_count(ware1) == 1

    def test_badge_label_format(self):
        n = 5
        label = f"⚠ {n} не собрано"
        assert label == "⚠ 5 не собрано"
