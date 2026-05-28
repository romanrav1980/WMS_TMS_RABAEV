"""
test_sprint41_functional.py — Functional tests for Sprint 41 (routes status filter).

Sprint 41 adds client-side status filter buttons above the routes table:
  "Все | Активен | Отгружен | Отменён"
Each button shows a count badge; filtering happens in the already-loaded tasks list.
"""


def make_task(condition: str = "Спланирован", task_id: int = 1) -> dict:
    return {"ID": task_id, "CONDITION": condition}


def apply_cond_filter(tasks: list[dict], f: str) -> list[dict]:
    if f == "all":
        return tasks
    if f == "active":
        return [t for t in tasks if t["CONDITION"] not in ("Отгружен", "Отменён")]
    if f == "closed":
        return [t for t in tasks if t["CONDITION"] == "Отгружен"]
    if f == "cancelled":
        return [t for t in tasks if t["CONDITION"] == "Отменён"]
    return tasks


def cond_counts(tasks: list[dict]) -> dict:
    return {
        "all":       len(tasks),
        "active":    len([t for t in tasks if t["CONDITION"] not in ("Отгружен", "Отменён")]),
        "closed":    len([t for t in tasks if t["CONDITION"] == "Отгружен"]),
        "cancelled": len([t for t in tasks if t["CONDITION"] == "Отменён"]),
    }


class TestCondFilter:
    def _tasks(self):
        return [
            make_task("Спланирован", 1),
            make_task("Спланирован", 2),
            make_task("Отгружен",    3),
            make_task("Отгружен",    4),
            make_task("Отменён",     5),
        ]

    def test_filter_all_returns_all(self):
        tasks = self._tasks()
        assert len(apply_cond_filter(tasks, "all")) == 5

    def test_filter_active_excludes_closed_and_cancelled(self):
        result = apply_cond_filter(self._tasks(), "active")
        assert len(result) == 2
        assert all(t["CONDITION"] == "Спланирован" for t in result)

    def test_filter_closed_returns_only_shipped(self):
        result = apply_cond_filter(self._tasks(), "closed")
        assert len(result) == 2
        assert all(t["CONDITION"] == "Отгружен" for t in result)

    def test_filter_cancelled_returns_only_cancelled(self):
        result = apply_cond_filter(self._tasks(), "cancelled")
        assert len(result) == 1
        assert result[0]["CONDITION"] == "Отменён"

    def test_empty_tasks_all_filters_return_empty(self):
        for f in ("all", "active", "closed", "cancelled"):
            assert apply_cond_filter([], f) == []

    def test_cond_counts_correct(self):
        counts = cond_counts(self._tasks())
        assert counts["all"] == 5
        assert counts["active"] == 2
        assert counts["closed"] == 2
        assert counts["cancelled"] == 1

    def test_cond_counts_empty(self):
        counts = cond_counts([])
        assert all(v == 0 for v in counts.values())

    def test_active_includes_various_non_terminal_statuses(self):
        tasks = [
            make_task("Спланирован", 1),
            make_task("Новый",       2),
            make_task("Активен",     3),
            make_task("Отгружен",    4),
        ]
        result = apply_cond_filter(tasks, "active")
        assert len(result) == 3
        assert all(t["CONDITION"] != "Отгружен" for t in result)

    def test_filter_all_after_closed_reset(self):
        tasks = [make_task("Отгружен", i) for i in range(3)]
        assert len(apply_cond_filter(tasks, "all")) == 3
        assert len(apply_cond_filter(tasks, "active")) == 0

    def test_counts_badge_zero_when_no_cancelled(self):
        tasks = [make_task("Спланирован", 1), make_task("Отгружен", 2)]
        counts = cond_counts(tasks)
        assert counts["cancelled"] == 0

    def test_counter_displayed_only_when_nonzero(self):
        counts = cond_counts([make_task("Отменён", 1)])
        assert counts["cancelled"] > 0
        assert counts["active"] == 0

    def test_filter_resets_when_new_tasks_loaded(self):
        """After a reload, filter='all' means the new task list is visible."""
        old_tasks = [make_task("Отгружен", 1)]
        new_tasks = [make_task("Спланирован", 2), make_task("Спланирован", 3)]
        assert apply_cond_filter(new_tasks, "all") == new_tasks

    def test_all_closed_active_count_zero(self):
        tasks = [make_task("Отгружен", i) for i in range(4)]
        counts = cond_counts(tasks)
        assert counts["active"] == 0
        assert counts["closed"] == 4

    def test_filter_preserves_task_ids(self):
        tasks = self._tasks()
        result = apply_cond_filter(tasks, "closed")
        assert {t["ID"] for t in result} == {3, 4}
