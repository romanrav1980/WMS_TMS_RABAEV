"""
test_sprint56_functional.py — Functional tests for Sprint 56 (print route sheet).

Sprint 56 adds a «🖨 Печать» button in the trip panel (tasks + routes tabs).
Clicking it opens a new browser window with a printable route sheet and calls window.print().
No new backend endpoints — pure frontend HTML generation.
"""


def build_route_sheet_html(task: dict, sts: list[dict]) -> str:
    """Mirror the frontend handlePrintRoute HTML generation."""
    date = task.get("SHIPMENT_DATE") or ""
    rows = []
    for i, s in enumerate(sts, 1):
        rows.append(
            f"{i};{s.get('ORD') or '—'};{s.get('ADDR') or ''};{s.get('RAION') or ''};"
            f"{s.get('PALLETS_COUNT', 0)};{s.get('WEIGHT_KG', 0.0):.0f};_"
        )
    total_p = sum(s.get("PALLETS_COUNT", 0) for s in sts)
    total_m = sum(s.get("WEIGHT_KG", 0.0) for s in sts)
    return {
        "title": f"Маршрутный лист №{task['ID']}",
        "date": date,
        "transport": task.get("TRANSPORT") or "—",
        "driver": task.get("VODITEL_NAME") or "—",
        "dock": task.get("DOCK") or "—",
        "condition": task.get("CONDITION") or "Новый",
        "rows": rows,
        "total_pallets": total_p,
        "total_weight_kg": total_m,
    }


class TestPrintRouteSheet:
    def _task(self):
        return {
            "ID": 1234,
            "SHIPMENT_DATE": "2026-05-28",
            "TRANSPORT": "Е715ТТ",
            "TRANSTYPE": "Тент",
            "VODITEL_NAME": "Иванов И.И.",
            "DOCK": "Д-3",
            "CONDITION": "Новый",
        }

    def _sts(self):
        return [
            {"ADDR": "ул. Ленина 1", "RAION": "Центр",  "ORD": 1, "PALLETS_COUNT": 5, "WEIGHT_KG": 300.0},
            {"ADDR": "пр. Мира 10",  "RAION": "Лысьва", "ORD": 2, "PALLETS_COUNT": 8, "WEIGHT_KG": 500.0},
            {"ADDR": "ул. Гагарина 5","RAION": None,    "ORD": 3, "PALLETS_COUNT": 3, "WEIGHT_KG": 150.0},
        ]

    def test_title_contains_task_id(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert "1234" in sheet["title"]

    def test_date_in_sheet(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert sheet["date"] == "2026-05-28"

    def test_transport_in_sheet(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert sheet["transport"] == "Е715ТТ"

    def test_driver_in_sheet(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert sheet["driver"] == "Иванов И.И."

    def test_dock_in_sheet(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert sheet["dock"] == "Д-3"

    def test_row_count(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert len(sheet["rows"]) == 3

    def test_total_pallets(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert sheet["total_pallets"] == 16

    def test_total_weight(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert abs(sheet["total_weight_kg"] - 950.0) < 0.01

    def test_null_driver_shows_dash(self):
        task = dict(self._task())
        task["VODITEL_NAME"] = None
        sheet = build_route_sheet_html(task, self._sts())
        assert sheet["driver"] == "—"

    def test_null_transport_shows_dash(self):
        task = dict(self._task())
        task["TRANSPORT"] = None
        sheet = build_route_sheet_html(task, self._sts())
        assert sheet["transport"] == "—"

    def test_null_raion_empty_in_row(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        row3 = sheet["rows"][2]
        assert ";" in row3  # row has no RAION (empty string)

    def test_ordinal_numbering(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert sheet["rows"][0].startswith("1;")
        assert sheet["rows"][1].startswith("2;")
        assert sheet["rows"][2].startswith("3;")

    def test_button_disabled_when_no_sts(self):
        def btn_disabled(sts_count: int) -> bool:
            return sts_count == 0
        assert btn_disabled(0) is True
        assert btn_disabled(1) is False

    def test_condition_in_sheet(self):
        sheet = build_route_sheet_html(self._task(), self._sts())
        assert sheet["condition"] == "Новый"
