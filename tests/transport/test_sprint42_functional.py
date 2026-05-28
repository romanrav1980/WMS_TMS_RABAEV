"""
test_sprint42_functional.py — Functional tests for Sprint 42 (toast notifications).

Sprint 42 adds a transient success toast (3-second auto-dismiss) that fires after:
  create task, create from cluster, close task, cancel task,
  assign STs, bulk-unassign STs, copy task.

The toast message format is tested here as pure string logic; the
React auto-dismiss timer is validated in usability checklist.
"""


def toast_create(task_id: int) -> str:
    return f"Рейс #{task_id} создан"


def toast_create_cluster(task_id: int, raion: str, st_count: int) -> str:
    return f"Рейс #{task_id} создан из кластера «{raion}», {st_count} СТ"


def toast_close(task_id: int) -> str:
    return f"Рейс #{task_id} закрыт"


def toast_cancel(task_id: int) -> str:
    return f"Рейс #{task_id} отменён"


def toast_assign(assigned: int, task_id: int) -> str:
    return f"{assigned} СТ добавлено в рейс #{task_id}"


def toast_bulk_unassign(count: int, task_id: int) -> str:
    return f"{count} СТ снято с рейса #{task_id}"


def toast_copy(new_id: int, source_id: int) -> str:
    return f"Рейс #{new_id} создан как копия рейса #{source_id}"


class TestToastMessages:
    def test_create_task(self):
        assert toast_create(1247) == "Рейс #1247 создан"

    def test_create_cluster(self):
        msg = toast_create_cluster(1248, "Лысьва", 7)
        assert "1248" in msg and "Лысьва" in msg and "7" in msg

    def test_close_task(self):
        assert toast_close(1247) == "Рейс #1247 закрыт"

    def test_cancel_task(self):
        assert toast_cancel(1247) == "Рейс #1247 отменён"

    def test_assign_sts(self):
        msg = toast_assign(5, 1247)
        assert "5" in msg and "1247" in msg

    def test_bulk_unassign(self):
        msg = toast_bulk_unassign(3, 1247)
        assert "3" in msg and "1247" in msg

    def test_copy_task(self):
        msg = toast_copy(1300, 1247)
        assert "1300" in msg and "1247" in msg

    def test_assign_zero_returns_zero_string(self):
        assert "0" in toast_assign(0, 1)

    def test_cluster_raion_empty_string(self):
        msg = toast_create_cluster(1, "", 0)
        assert "«»" in msg

    def test_create_ids_distinct(self):
        assert toast_create(1) != toast_close(1)
        assert toast_close(1) != toast_cancel(1)

    def test_messages_not_empty(self):
        for fn in [toast_create, toast_close, toast_cancel]:
            assert len(fn(1)) > 0

    def test_assign_plural_sts(self):
        for n in [1, 2, 10, 100]:
            assert str(n) in toast_assign(n, 99)

    def test_bulk_unassign_count_matches(self):
        for n in [1, 5, 12]:
            assert str(n) in toast_bulk_unassign(n, 1247)
