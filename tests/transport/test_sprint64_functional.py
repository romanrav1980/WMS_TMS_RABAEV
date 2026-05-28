"""
test_sprint64_functional.py — Functional tests for Sprint 64 (click-to-select not-ready STs).

Sprint 64 upgrades the «⚠ N не собрано» badge from Sprint 63 into a button:
clicking it adds all not-ready STs (VERIFY_PERC < 100) to the selection set.
The badge uses setSelectedStNums(prev => new Set([...prev, ...notReadySts.map(s => s.ST_NUMBER)])).
"""


def select_not_ready(existing: set[str], sts: list[dict]) -> set[str]:
    """Mirror the onClick handler logic."""
    result = set(existing)
    for s in sts:
        if s.get("VERIFY_PERC") is not None and s["VERIFY_PERC"] < 100:
            result.add(s["ST_NUMBER"])
    return result


class TestSelectNotReady:
    def _sts(self):
        return [
            {"ST_NUMBER": "A1", "VERIFY_PERC": 100},
            {"ST_NUMBER": "A2", "VERIFY_PERC": 75},
            {"ST_NUMBER": "A3", "VERIFY_PERC": 0},
            {"ST_NUMBER": "A4", "VERIFY_PERC": None},
            {"ST_NUMBER": "A5", "VERIFY_PERC": 100},
        ]

    def test_adds_incomplete_sts_to_selection(self):
        result = select_not_ready(set(), self._sts())
        assert "A2" in result
        assert "A3" in result

    def test_does_not_add_complete_sts(self):
        result = select_not_ready(set(), self._sts())
        assert "A1" not in result
        assert "A5" not in result

    def test_does_not_add_null_perc_sts(self):
        result = select_not_ready(set(), self._sts())
        assert "A4" not in result

    def test_preserves_existing_selection(self):
        existing = {"B1", "B2"}
        result = select_not_ready(existing, self._sts())
        assert "B1" in result
        assert "B2" in result

    def test_idempotent_when_all_already_selected(self):
        existing = {"A2", "A3"}
        result = select_not_ready(existing, self._sts())
        assert result == {"A2", "A3"}

    def test_empty_sts_list(self):
        result = select_not_ready(set(), [])
        assert result == set()

    def test_all_assembled_adds_nothing(self):
        sts = [{"ST_NUMBER": f"X{i}", "VERIFY_PERC": 100} for i in range(5)]
        result = select_not_ready(set(), sts)
        assert result == set()

    def test_zero_perc_included(self):
        sts = [{"ST_NUMBER": "Z1", "VERIFY_PERC": 0}]
        result = select_not_ready(set(), sts)
        assert "Z1" in result

    def test_99_perc_included(self):
        sts = [{"ST_NUMBER": "Z2", "VERIFY_PERC": 99}]
        result = select_not_ready(set(), sts)
        assert "Z2" in result

    def test_result_is_new_set(self):
        """Original set must not be mutated."""
        original = {"X"}
        result = select_not_ready(original, self._sts())
        assert result is not original
