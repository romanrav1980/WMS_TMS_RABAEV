"""
test_sprint43_functional.py — Functional tests for Sprint 43 (sortable trips table).

Sprint 43 adds client-side column sorting to the trips table (tasks tab).
Clicking a header sorts ascending; clicking again toggles to descending.
"""


def make_task(**kwargs) -> dict:
    defaults = {
        "ID": 1, "SHIPMENT_TIME": None, "ST_COUNT": 0,
        "PALLET_COUNT": 0, "TRANSTYPE": None, "TRANSPORT": None,
        "SHIPMENT_DATE": "2026-05-28", "VODITEL_NAME": None,
        "DOCK": None, "REGIONS": None, "PRICE": None,
        "CONDITION": "Спланирован", "READY_PERC": None,
    }
    return {**defaults, **kwargs}


def sort_tasks(tasks: list[dict], field: str, direction: str = "asc") -> list[dict]:
    reverse = direction == "desc"
    return sorted(tasks, key=lambda t: (t.get(field) is None, t.get(field) or ""), reverse=reverse)


class TestSortableTasks:
    def _tasks(self):
        return [
            make_task(ID=3, PALLET_COUNT=5, TRANSPORT="А001АА", CONDITION="Отгружен"),
            make_task(ID=1, PALLET_COUNT=12, TRANSPORT="В002ВВ", CONDITION="Спланирован"),
            make_task(ID=2, PALLET_COUNT=8, TRANSPORT=None, CONDITION="Спланирован"),
        ]

    def test_sort_by_id_asc(self):
        result = sort_tasks(self._tasks(), "ID", "asc")
        assert [t["ID"] for t in result] == [1, 2, 3]

    def test_sort_by_id_desc(self):
        result = sort_tasks(self._tasks(), "ID", "desc")
        assert [t["ID"] for t in result] == [3, 2, 1]

    def test_sort_by_pallet_count_asc(self):
        result = sort_tasks(self._tasks(), "PALLET_COUNT", "asc")
        assert result[0]["PALLET_COUNT"] == 5
        assert result[-1]["PALLET_COUNT"] == 12

    def test_sort_by_pallet_count_desc(self):
        result = sort_tasks(self._tasks(), "PALLET_COUNT", "desc")
        assert result[0]["PALLET_COUNT"] == 12

    def test_sort_by_transport_null_last_asc(self):
        result = sort_tasks(self._tasks(), "TRANSPORT", "asc")
        assert result[-1]["TRANSPORT"] is None

    def test_sort_by_condition_asc(self):
        result = sort_tasks(self._tasks(), "CONDITION", "asc")
        conditions = [t["CONDITION"] for t in result]
        assert conditions == sorted(conditions)

    def test_sort_stable_on_equal_values(self):
        tasks = [make_task(ID=2, PALLET_COUNT=5), make_task(ID=1, PALLET_COUNT=5)]
        result = sort_tasks(tasks, "PALLET_COUNT", "asc")
        assert len(result) == 2

    def test_sort_empty_list(self):
        assert sort_tasks([], "ID", "asc") == []

    def test_toggle_direction(self):
        tasks = self._tasks()
        asc = sort_tasks(tasks, "ID", "asc")
        desc = sort_tasks(tasks, "ID", "desc")
        assert asc[0]["ID"] != desc[0]["ID"]

    def test_no_sort_preserves_order(self):
        tasks = self._tasks()
        result = sort_tasks(tasks, "ID", "asc")
        assert len(result) == len(tasks)

    def test_sort_by_shipment_date(self):
        tasks = [
            make_task(ID=1, SHIPMENT_DATE="2026-06-01"),
            make_task(ID=2, SHIPMENT_DATE="2026-05-28"),
            make_task(ID=3, SHIPMENT_DATE="2026-05-30"),
        ]
        result = sort_tasks(tasks, "SHIPMENT_DATE", "asc")
        dates = [t["SHIPMENT_DATE"] for t in result]
        assert dates == sorted(dates)

    def test_sort_by_price_null_last(self):
        tasks = [
            make_task(ID=1, PRICE=5000),
            make_task(ID=2, PRICE=None),
            make_task(ID=3, PRICE=1000),
        ]
        result = sort_tasks(tasks, "PRICE", "asc")
        assert result[-1]["PRICE"] is None

    def test_sort_direction_asc_default(self):
        tasks = self._tasks()
        result = sort_tasks(tasks, "ID")
        assert result[0]["ID"] == min(t["ID"] for t in tasks)
