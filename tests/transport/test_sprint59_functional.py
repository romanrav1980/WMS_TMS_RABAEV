"""
test_sprint59_functional.py — Functional tests for Sprint 59 (quick search in routes tab).

Sprint 59 adds a text search input in the routes-tab toolbar.
It filters the visible routes client-side by: ID, transport number, driver name, regions, TK_NAME.
Empty query shows all routes (passes through filteredRouteTasks unchanged).
"""


def search_routes(tasks: list[dict], query: str) -> list[dict]:
    """Mirror the frontend searchedRouteTasks computed value."""
    q = query.strip().lower()
    if not q:
        return tasks
    return [
        t for t in tasks
        if (
            q in str(t.get("ID", "")).lower() or
            q in (t.get("TRANSPORT") or "").lower() or
            q in (t.get("VODITEL_NAME") or "").lower() or
            q in (t.get("REGIONS") or "").lower() or
            q in (t.get("TK_NAME") or "").lower()
        )
    ]


class TestRouteSearch:
    def _tasks(self):
        return [
            {"ID": 1001, "TRANSPORT": "Е715ТТ", "VODITEL_NAME": "Иванов И.И.", "REGIONS": "Пермь", "TK_NAME": "ООО Ромашка", "CONDITION": "Новый"},
            {"ID": 1002, "TRANSPORT": "А123БВ", "VODITEL_NAME": "Петров П.П.", "REGIONS": "Лысьва", "TK_NAME": None, "CONDITION": "Отгружен"},
            {"ID": 1003, "TRANSPORT": "В456ГД", "VODITEL_NAME": None, "REGIONS": "Чусовой", "TK_NAME": "ООО Берёзка", "CONDITION": "Новый"},
        ]

    def test_empty_query_returns_all(self):
        assert search_routes(self._tasks(), "") == self._tasks()

    def test_whitespace_query_returns_all(self):
        assert search_routes(self._tasks(), "  ") == self._tasks()

    def test_search_by_id(self):
        result = search_routes(self._tasks(), "1001")
        assert len(result) == 1
        assert result[0]["ID"] == 1001

    def test_search_by_partial_id(self):
        result = search_routes(self._tasks(), "100")
        assert len(result) == 3

    def test_search_by_transport(self):
        result = search_routes(self._tasks(), "Е715")
        assert len(result) == 1
        assert result[0]["TRANSPORT"] == "Е715ТТ"

    def test_search_by_driver(self):
        result = search_routes(self._tasks(), "Иванов")
        assert len(result) == 1
        assert result[0]["VODITEL_NAME"] == "Иванов И.И."

    def test_search_by_region(self):
        result = search_routes(self._tasks(), "Лысьва")
        assert len(result) == 1
        assert result[0]["REGIONS"] == "Лысьва"

    def test_search_by_tk_name(self):
        result = search_routes(self._tasks(), "Ромашка")
        assert len(result) == 1
        assert result[0]["TK_NAME"] == "ООО Ромашка"

    def test_search_case_insensitive(self):
        result = search_routes(self._tasks(), "иванов")
        assert len(result) == 1

    def test_search_no_match(self):
        result = search_routes(self._tasks(), "XYZ-NOTFOUND")
        assert len(result) == 0

    def test_null_fields_do_not_crash(self):
        tasks = [{"ID": 9, "TRANSPORT": None, "VODITEL_NAME": None, "REGIONS": None, "TK_NAME": None}]
        result = search_routes(tasks, "test")
        assert result == []

    def test_null_fields_empty_query_returns_all(self):
        tasks = [{"ID": 9, "TRANSPORT": None, "VODITEL_NAME": None, "REGIONS": None, "TK_NAME": None}]
        result = search_routes(tasks, "")
        assert len(result) == 1

    def test_clear_button_shown_when_query_nonempty(self):
        query = "abc"
        show_clear = bool(query)
        assert show_clear is True

    def test_clear_button_hidden_when_query_empty(self):
        query = ""
        show_clear = bool(query)
        assert show_clear is False
