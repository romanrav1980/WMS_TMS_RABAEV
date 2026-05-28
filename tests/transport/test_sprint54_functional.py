"""
test_sprint54_functional.py — Functional tests for Sprint 54 (CSV export of selected STs).

Sprint 54 adds a «⬇ CSV» button in the sticky sel-bar that downloads
the currently-selected STs as a CSV file (BOM UTF-8, semicolon-delimited).
"""


def export_selected_sts_csv(sts: list[dict], date: str) -> str:
    """Mirror the frontend exportSelectedStsCsv logic."""
    BOM = "﻿"
    header = "СТ №;Адрес;Регион;Район;Паллет;Вес кг;Объём м³;% сборки;Тип ТС;Рейс"
    rows = []
    for s in sts:
        vp = s.get("VERIFY_PERC")
        perc = f"{vp * 100:.0f}%" if vp is not None else ""
        transtask = f"#{s['TRANSTASK_ID']}" if s.get("TRANSTASK_ID") else ""
        rows.append(";".join([
            str(s["ST_NUMBER"]),
            s.get("ADDR") or "",
            s.get("REGION") or "",
            s.get("RAION") or "",
            str(s.get("PALLETS_COUNT", 0)),
            str(s.get("WEIGHT_KG", 0)),
            f"{(s.get('VOLUME_M3') or 0):.2f}",
            perc,
            s.get("TRANSPORT_TYPE") or "",
            transtask,
        ]))
    total_p = sum(s.get("PALLETS_COUNT", 0) for s in sts)
    total_m = sum(s.get("WEIGHT_KG", 0) for s in sts)
    rows.append(f"ИТОГО;;;;{total_p};{total_m:.0f};;;;")
    return BOM + "\n".join([header] + rows)


class TestExportSelectedStsCsv:
    def _sts(self):
        return [
            {"ST_NUMBER": "ST-001", "ADDR": "ул. Ленина 1", "REGION": "Пермь", "RAION": "Центр",
             "PALLETS_COUNT": 5, "WEIGHT_KG": 300.0, "VOLUME_M3": 2.5,
             "VERIFY_PERC": 1.0, "TRANSPORT_TYPE": "Тент", "TRANSTASK_ID": None},
            {"ST_NUMBER": "ST-002", "ADDR": "пр. Мира 10", "REGION": "Лысьва", "RAION": None,
             "PALLETS_COUNT": 8, "WEIGHT_KG": 500.0, "VOLUME_M3": 3.0,
             "VERIFY_PERC": 0.5, "TRANSPORT_TYPE": "Реф", "TRANSTASK_ID": 42},
        ]

    def test_bom_present(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        assert csv.startswith("﻿")

    def test_header_row(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        lines = csv.lstrip("﻿").split("\n")
        assert lines[0] == "СТ №;Адрес;Регион;Район;Паллет;Вес кг;Объём м³;% сборки;Тип ТС;Рейс"

    def test_data_rows_count(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        lines = csv.lstrip("﻿").split("\n")
        assert len(lines) == 4  # header + 2 rows + totals

    def test_st_number_in_row(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        assert "ST-001" in csv

    def test_transtask_id_formatted(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        assert "#42" in csv

    def test_no_transtask_empty_string(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        lines = csv.lstrip("﻿").split("\n")
        row1 = lines[1].split(";")
        assert row1[-1] == ""  # no trip

    def test_verify_perc_formatted(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        assert "100%" in csv
        assert "50%" in csv

    def test_null_verify_perc_empty(self):
        sts = [{"ST_NUMBER": "X", "PALLETS_COUNT": 1, "WEIGHT_KG": 10.0,
                "VOLUME_M3": 1.0, "VERIFY_PERC": None, "TRANSTASK_ID": None}]
        csv = export_selected_sts_csv(sts, "2026-05-28")
        lines = csv.lstrip("﻿").split("\n")
        row = lines[1].split(";")
        assert row[7] == ""

    def test_totals_row(self):
        csv = export_selected_sts_csv(self._sts(), "2026-05-28")
        lines = csv.lstrip("﻿").split("\n")
        totals = lines[-1]
        assert "ИТОГО" in totals
        assert "13" in totals   # total pallets = 5 + 8
        assert "800" in totals  # total weight = 300 + 500

    def test_null_addr_empty_string(self):
        sts = [{"ST_NUMBER": "A", "ADDR": None, "PALLETS_COUNT": 1, "WEIGHT_KG": 5.0,
                "VOLUME_M3": None, "VERIFY_PERC": None, "TRANSTASK_ID": None}]
        csv = export_selected_sts_csv(sts, "2026-05-28")
        lines = csv.lstrip("﻿").split("\n")
        row = lines[1].split(";")
        assert row[1] == ""

    def test_null_volume_treated_as_zero(self):
        sts = [{"ST_NUMBER": "B", "PALLETS_COUNT": 2, "WEIGHT_KG": 20.0,
                "VOLUME_M3": None, "VERIFY_PERC": None, "TRANSTASK_ID": None}]
        csv = export_selected_sts_csv(sts, "2026-05-28")
        assert "0.00" in csv

    def test_single_st_export(self):
        sts = [self._sts()[0]]
        csv = export_selected_sts_csv(sts, "2026-05-28")
        lines = csv.lstrip("﻿").split("\n")
        assert len(lines) == 3  # header + 1 row + totals
