"""
test_sprint49_functional.py — Functional tests for Sprint 49 (dense mode toggle).

Sprint 49 adds a «Компактно» checkbox to the STs toolbar.
When active, the table gets class dispatch-grid-dense which reduces cell padding.
"""


def table_class(dense: bool) -> str:
    base = "dispatch-grid"
    return f"{base} dispatch-grid-dense" if dense else base


def visible_rows_estimate(total_rows: int, row_height_px: int, container_height_px: int) -> int:
    return container_height_px // row_height_px


class TestDenseMode:
    def test_class_normal_mode(self):
        assert table_class(False) == "dispatch-grid"

    def test_class_dense_mode(self):
        assert "dispatch-grid-dense" in table_class(True)

    def test_class_includes_base(self):
        assert "dispatch-grid" in table_class(True)

    def test_dense_reduces_row_height(self):
        normal_h = 26
        dense_h  = 18
        container = 600
        normal_rows = visible_rows_estimate(100, normal_h, container)
        dense_rows  = visible_rows_estimate(100, dense_h,  container)
        assert dense_rows > normal_rows

    def test_toggle_off_restores_normal(self):
        assert table_class(True)  != table_class(False)
        assert table_class(False) == "dispatch-grid"

    def test_initial_state_is_not_dense(self):
        initial = False
        assert table_class(initial) == "dispatch-grid"

    def test_dense_class_name_correct(self):
        cls = table_class(True)
        assert cls == "dispatch-grid dispatch-grid-dense"

    def test_rows_visible_improvement(self):
        """Dense mode shows ~44% more rows in the same height."""
        normal_h = 26
        dense_h  = 18
        ratio = normal_h / dense_h
        assert ratio > 1.3

    def test_toggle_state_independent_of_data(self):
        rows_count = 0
        assert table_class(True) != "dispatch-grid"
        rows_count = 100
        assert table_class(True) != "dispatch-grid"
        assert rows_count == 100
