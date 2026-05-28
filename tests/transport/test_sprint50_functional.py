"""
test_sprint50_functional.py — Functional tests for Sprint 50 (ready-ST highlight).

Sprint 50 adds class dispatch-st-ready (green left border) to ST rows
where VERIFY_PERC === 1.0 and the row is not selected (checked).
"""


def st_row_class(
    ware_id: int = 5,
    verify_perc: float | None = None,
    checked: bool = False,
    is_child: bool = False,
) -> str:
    ware_classes = {5: "dispatch-ware-5", 6: "dispatch-ware-6", 7: "dispatch-ware-7"}
    ware_cls = ware_classes.get(ware_id, "")
    parts = [
        "dispatch-gr",
        "selected" if checked else ware_cls,
        "dispatch-st-ready" if not checked and verify_perc == 1.0 else "",
        "dispatch-grid-cluster-child" if is_child else "",
    ]
    return " ".join(p for p in parts if p)


class TestReadyHighlight:
    def test_ready_class_when_verify_100(self):
        cls = st_row_class(verify_perc=1.0, checked=False)
        assert "dispatch-st-ready" in cls

    def test_no_ready_class_when_partial(self):
        cls = st_row_class(verify_perc=0.5, checked=False)
        assert "dispatch-st-ready" not in cls

    def test_no_ready_class_when_zero(self):
        cls = st_row_class(verify_perc=0.0, checked=False)
        assert "dispatch-st-ready" not in cls

    def test_no_ready_class_when_none(self):
        cls = st_row_class(verify_perc=None, checked=False)
        assert "dispatch-st-ready" not in cls

    def test_no_ready_class_when_selected(self):
        cls = st_row_class(verify_perc=1.0, checked=True)
        assert "dispatch-st-ready" not in cls

    def test_selected_takes_priority_over_ware(self):
        cls = st_row_class(ware_id=7, checked=True)
        assert "selected" in cls
        assert "dispatch-ware-7" not in cls

    def test_ware_class_when_not_selected_and_not_ready(self):
        cls = st_row_class(ware_id=5, verify_perc=0.5, checked=False)
        assert "dispatch-ware-5" in cls
        assert "dispatch-st-ready" not in cls

    def test_ready_and_ware_class_coexist(self):
        cls = st_row_class(ware_id=5, verify_perc=1.0, checked=False)
        assert "dispatch-ware-5" in cls
        assert "dispatch-st-ready" in cls

    def test_child_class_appended(self):
        cls = st_row_class(is_child=True)
        assert "dispatch-grid-cluster-child" in cls

    def test_base_class_always_present(self):
        for checked in (True, False):
            cls = st_row_class(checked=checked)
            assert "dispatch-gr" in cls

    def test_ready_with_ware_7(self):
        cls = st_row_class(ware_id=7, verify_perc=1.0, checked=False)
        assert "dispatch-ware-7" in cls
        assert "dispatch-st-ready" in cls

    def test_ready_class_not_shown_for_verify_0_99(self):
        for perc in [0.0, 0.5, 0.99, 0.999]:
            cls = st_row_class(verify_perc=perc, checked=False)
            assert "dispatch-st-ready" not in cls, f"failed for perc={perc}"
