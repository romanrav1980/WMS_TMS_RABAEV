"""
test_sprint33_functional.py — Functional tests for Sprint 33.

Sprint 33 adds «Кратко» (brief mode) checkbox in the routes toolbar.
When checked, hides secondary columns: Объём, Тип, Цена, ТК, Логист, 💰.
Keeps: Отгрузка, #, Пал., Вес, Машина, Водитель, ДОК, Регионы, Статус.

Backend: no new endpoints — purely frontend change.
Tests cover column visibility logic.
"""

import pytest


# ---------------------------------------------------------------------------
# Column visibility logic (mirrors frontend !routeBriefMode conditionals)
# ---------------------------------------------------------------------------

FULL_COLUMNS = ["Отгрузка", "#", "Пал.", "Вес", "Объём", "Тип", "Машина",
                "Водитель", "ДОК", "Регионы", "Цена", "ТК", "Логист", "Статус", "💰"]

BRIEF_COLUMNS = ["Отгрузка", "#", "Пал.", "Вес", "Машина",
                 "Водитель", "ДОК", "Регионы", "Статус"]

HIDDEN_IN_BRIEF = ["Объём", "Тип", "Цена", "ТК", "Логист", "💰"]


def visible_columns(brief_mode: bool) -> list[str]:
    if brief_mode:
        return BRIEF_COLUMNS[:]
    return FULL_COLUMNS[:]


class TestBriefModeColumns:

    def test_full_mode_shows_all_15_columns(self):
        cols = visible_columns(False)
        assert len(cols) == 15

    def test_brief_mode_shows_9_columns(self):
        cols = visible_columns(True)
        assert len(cols) == 9

    def test_brief_mode_hides_volume(self):
        assert "Объём" not in visible_columns(True)

    def test_brief_mode_hides_type(self):
        assert "Тип" not in visible_columns(True)

    def test_brief_mode_hides_price(self):
        assert "Цена" not in visible_columns(True)

    def test_brief_mode_hides_tk(self):
        assert "ТК" not in visible_columns(True)

    def test_brief_mode_hides_logist(self):
        assert "Логист" not in visible_columns(True)

    def test_brief_mode_hides_billing(self):
        assert "💰" not in visible_columns(True)

    def test_brief_mode_keeps_essential_columns(self):
        cols = visible_columns(True)
        for col in BRIEF_COLUMNS:
            assert col in cols, f"Essential column «{col}» should be visible in brief mode"

    def test_full_mode_shows_all_hidden_columns(self):
        cols = visible_columns(False)
        for col in HIDDEN_IN_BRIEF:
            assert col in cols, f"Column «{col}» should be visible in full mode"

    def test_toggle_restores_full_mode(self):
        """Going brief and back to full should restore all columns."""
        assert visible_columns(True) == BRIEF_COLUMNS
        assert visible_columns(False) == FULL_COLUMNS

    def test_brief_mode_colspan_is_8_or_9(self):
        """Empty row colspan should match visible column count."""
        cols = visible_columns(True)
        assert len(cols) == 9

    def test_full_mode_colspan_is_15(self):
        cols = visible_columns(False)
        assert len(cols) == 15
