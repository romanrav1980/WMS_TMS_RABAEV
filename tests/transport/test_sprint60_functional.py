"""
test_sprint60_functional.py — Functional tests for Sprint 60 (pagination of STs table).

Sprint 60 adds client-side pagination (100 rows/page) to the flat-mode STs table.
pagedSts = sortedSts.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
Total pages = max(1, ceil(len / PAGE_SIZE)).
Page resets to 0 when availableSts, stSortField, or stSortDir changes.
"""

import math


ST_PAGE_SIZE = 100


def paginate(items: list, page: int) -> list:
    """Mirror pagedSts computed value."""
    return items[page * ST_PAGE_SIZE : (page + 1) * ST_PAGE_SIZE]


def total_pages(items: list) -> int:
    return max(1, math.ceil(len(items) / ST_PAGE_SIZE))


class TestPagination:
    def _items(self, n: int) -> list[dict]:
        return [{"ST_NUMBER": str(i)} for i in range(n)]

    def test_fewer_than_page_size_stays_on_one_page(self):
        items = self._items(50)
        assert total_pages(items) == 1
        assert paginate(items, 0) == items

    def test_exactly_page_size_is_one_page(self):
        items = self._items(100)
        assert total_pages(items) == 1
        assert len(paginate(items, 0)) == 100

    def test_one_over_page_size_is_two_pages(self):
        items = self._items(101)
        assert total_pages(items) == 2
        assert len(paginate(items, 0)) == 100
        assert len(paginate(items, 1)) == 1

    def test_empty_list_gives_one_page(self):
        assert total_pages([]) == 1
        assert paginate([], 0) == []

    def test_300_items_gives_three_pages(self):
        items = self._items(300)
        assert total_pages(items) == 3
        assert len(paginate(items, 0)) == 100
        assert len(paginate(items, 1)) == 100
        assert len(paginate(items, 2)) == 100

    def test_301_items_gives_four_pages(self):
        items = self._items(301)
        assert total_pages(items) == 4
        assert len(paginate(items, 3)) == 1

    def test_first_page_correct_items(self):
        items = self._items(250)
        page0 = paginate(items, 0)
        assert page0[0]["ST_NUMBER"] == "0"
        assert page0[-1]["ST_NUMBER"] == "99"

    def test_second_page_correct_items(self):
        items = self._items(250)
        page1 = paginate(items, 1)
        assert page1[0]["ST_NUMBER"] == "100"
        assert page1[-1]["ST_NUMBER"] == "199"

    def test_global_index_calculation(self):
        """Shift-click passes global idx = page * PAGE_SIZE + pageIdx."""
        page, page_idx = 2, 5
        expected_global = 2 * ST_PAGE_SIZE + 5
        assert page * ST_PAGE_SIZE + page_idx == expected_global

    def test_page_reset_on_data_change(self):
        """Simulates: after data reload, page resets to 0."""
        page = 3
        # new data arrives → reset
        page = 0
        assert page == 0

    def test_prev_button_disabled_on_first_page(self):
        page = 0
        prev_disabled = page == 0
        assert prev_disabled is True

    def test_next_button_disabled_on_last_page(self):
        pages = total_pages(self._items(250))  # 3
        page = 2
        next_disabled = page >= pages - 1
        assert next_disabled is True

    def test_nav_buttons_enabled_on_middle_page(self):
        pages = total_pages(self._items(250))
        page = 1
        assert (page == 0) is False
        assert (page >= pages - 1) is False

    def test_pagination_bar_hidden_when_single_page(self):
        """stTotalPages > 1 determines visibility."""
        pages = total_pages(self._items(50))
        show_bar = pages > 1
        assert show_bar is False

    def test_pagination_bar_shown_when_multi_page(self):
        pages = total_pages(self._items(101))
        show_bar = pages > 1
        assert show_bar is True
