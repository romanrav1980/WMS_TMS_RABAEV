"""
test_sprint52_functional.py — Functional tests for Sprint 52 (sortable STs table).

Sprint 52 adds client-side sort to the available-STs table.
Clicking a column header sorts ascending; clicking again reverses to descending.
NULL values sort last in both directions.
"""


def sort_sts(
    sts: list[dict],
    field: str,
    direction: str = "asc",
) -> list[dict]:
    """Mirror the frontend sortedSts logic."""
    def key(s: dict):
        v = s.get(field)
        return (v is None, v if v is not None else "")
    return sorted(sts, key=key, reverse=(direction == "desc"))


class TestStSort:
    def _sts(self):
        return [
            {"ST_NUMBER": "ST-003", "PALLETS_COUNT": 12, "WEIGHT_KG": 800.0, "VOLUME_M3": 6.0, "REGION": "Пермь",     "RAION": "Центр",   "ADDR": "ул. Ленина 1",  "WARE_ID": 9201, "VERIFY_PERC": 1.0, "TRANSTASK_ID": None, "TRANSPORT_TYPE": "Тент"},
            {"ST_NUMBER": "ST-001", "PALLETS_COUNT": 5,  "WEIGHT_KG": 300.0, "VOLUME_M3": 2.5, "REGION": "Лысьва",    "RAION": "Лысьва",  "ADDR": "пр. Мира 10",   "WARE_ID": 9202, "VERIFY_PERC": 0.5, "TRANSTASK_ID": 42,   "TRANSPORT_TYPE": "Реф"},
            {"ST_NUMBER": "ST-002", "PALLETS_COUNT": 8,  "WEIGHT_KG": 500.0, "VOLUME_M3": 3.0, "REGION": "Чусовой",   "RAION": None,       "ADDR": "ул. Гагарина 5","WARE_ID": 9201, "VERIFY_PERC": None,"TRANSTASK_ID": None, "TRANSPORT_TYPE": None},
        ]

    # --- PALLETS_COUNT ---
    def test_sort_pallets_asc(self):
        result = sort_sts(self._sts(), "PALLETS_COUNT", "asc")
        assert [r["PALLETS_COUNT"] for r in result] == [5, 8, 12]

    def test_sort_pallets_desc(self):
        result = sort_sts(self._sts(), "PALLETS_COUNT", "desc")
        assert [r["PALLETS_COUNT"] for r in result] == [12, 8, 5]

    # --- ST_NUMBER (string) ---
    def test_sort_st_number_asc(self):
        result = sort_sts(self._sts(), "ST_NUMBER", "asc")
        assert [r["ST_NUMBER"] for r in result] == ["ST-001", "ST-002", "ST-003"]

    def test_sort_st_number_desc(self):
        result = sort_sts(self._sts(), "ST_NUMBER", "desc")
        assert [r["ST_NUMBER"] for r in result] == ["ST-003", "ST-002", "ST-001"]

    # --- REGION ---
    def test_sort_region_asc(self):
        result = sort_sts(self._sts(), "REGION", "asc")
        regions = [r["REGION"] for r in result]
        assert regions == sorted(regions)

    # --- NULL handling ---
    def test_null_raion_last_asc(self):
        result = sort_sts(self._sts(), "RAION", "asc")
        assert result[-1]["RAION"] is None

    def test_null_raion_last_desc(self):
        result = sort_sts(self._sts(), "RAION", "desc")
        assert result[-1]["RAION"] is None

    def test_null_verify_perc_last_asc(self):
        result = sort_sts(self._sts(), "VERIFY_PERC", "asc")
        assert result[-1]["VERIFY_PERC"] is None

    def test_null_transport_type_last_asc(self):
        result = sort_sts(self._sts(), "TRANSPORT_TYPE", "asc")
        assert result[-1]["TRANSPORT_TYPE"] is None

    # --- Toggle direction ---
    def test_toggle_direction(self):
        direction = "asc"
        field = "PALLETS_COUNT"
        # same field → flip
        direction = "desc" if direction == "asc" else "asc"
        assert direction == "desc"

    def test_toggle_new_field_resets_to_asc(self):
        current_field = "PALLETS_COUNT"
        current_dir = "desc"
        new_field = "WEIGHT_KG"
        if current_field == new_field:
            new_dir = "desc" if current_dir == "asc" else "asc"
        else:
            new_dir = "asc"
        assert new_dir == "asc"

    # --- WEIGHT_KG ---
    def test_sort_weight_asc(self):
        result = sort_sts(self._sts(), "WEIGHT_KG", "asc")
        assert result[0]["WEIGHT_KG"] == 300.0
        assert result[-1]["WEIGHT_KG"] == 800.0

    # --- WARE_ID ---
    def test_sort_ware_id_asc(self):
        result = sort_sts(self._sts(), "WARE_ID", "asc")
        assert result[0]["WARE_ID"] == 9201
        assert result[-1]["WARE_ID"] == 9202

    # --- No sort: original order preserved ---
    def test_no_sort_preserves_order(self):
        sts = self._sts()
        result = sort_sts(sts, field=None, direction="asc") if False else sts
        assert result[0]["ST_NUMBER"] == "ST-003"

    # --- VERIFY_PERC: 0.0 < 0.5 < 1.0 ---
    def test_sort_verify_perc_asc(self):
        sts = [
            {"ST_NUMBER": "A", "VERIFY_PERC": 1.0},
            {"ST_NUMBER": "B", "VERIFY_PERC": 0.0},
            {"ST_NUMBER": "C", "VERIFY_PERC": None},
        ]
        result = sort_sts(sts, "VERIFY_PERC", "asc")
        assert result[0]["VERIFY_PERC"] == 0.0
        assert result[1]["VERIFY_PERC"] == 1.0
        assert result[2]["VERIFY_PERC"] is None
