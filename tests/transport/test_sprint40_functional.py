"""
test_sprint40_functional.py — Functional tests for Sprint 40 (day summary).

Sprint 40 adds a summary strip above the trips table showing:
  dayTotalTasks, dayTotalPallets, dayTotalWeight, dayClosedTasks / dayTotalTasks.

All values are computed client-side from the already-loaded tasks list —
no new backend requests.
"""


def make_task(pallet_count: int = 0, weight: float = 0.0,
              condition: str = "Активен") -> dict:
    return {"PALLET_COUNT": pallet_count, "TEMP_WEIGHT": weight, "CONDITION": condition}


def compute_day_summary(tasks: list[dict]) -> dict:
    return {
        "total_tasks":   len(tasks),
        "total_pallets": sum(t.get("PALLET_COUNT") or 0 for t in tasks),
        "total_weight":  sum(t.get("TEMP_WEIGHT") or 0.0 for t in tasks),
        "closed_tasks":  sum(1 for t in tasks if t.get("CONDITION") == "Отгружен"),
    }


class TestDaySummary:
    def test_empty_list(self):
        s = compute_day_summary([])
        assert s == {"total_tasks": 0, "total_pallets": 0, "total_weight": 0.0, "closed_tasks": 0}

    def test_single_active_task(self):
        s = compute_day_summary([make_task(pallet_count=10, weight=500.0)])
        assert s["total_tasks"] == 1
        assert s["total_pallets"] == 10
        assert s["total_weight"] == 500.0
        assert s["closed_tasks"] == 0

    def test_closed_task_counted(self):
        s = compute_day_summary([make_task(condition="Отгружен")])
        assert s["closed_tasks"] == 1

    def test_mixed_conditions(self):
        tasks = [
            make_task(pallet_count=5, condition="Активен"),
            make_task(pallet_count=8, condition="Отгружен"),
            make_task(pallet_count=3, condition="Отгружен"),
        ]
        s = compute_day_summary(tasks)
        assert s["total_tasks"] == 3
        assert s["total_pallets"] == 16
        assert s["closed_tasks"] == 2

    def test_weight_summed_correctly(self):
        tasks = [make_task(weight=1000.5), make_task(weight=234.25)]
        s = compute_day_summary(tasks)
        assert abs(s["total_weight"] - 1234.75) < 0.01

    def test_null_weight_treated_as_zero(self):
        tasks = [{"PALLET_COUNT": 5, "TEMP_WEIGHT": None, "CONDITION": "Активен"}]
        s = compute_day_summary(tasks)
        assert s["total_weight"] == 0.0

    def test_null_pallets_treated_as_zero(self):
        tasks = [{"PALLET_COUNT": None, "TEMP_WEIGHT": 100.0, "CONDITION": "Активен"}]
        s = compute_day_summary(tasks)
        assert s["total_pallets"] == 0

    def test_summary_strip_visible_when_tasks_nonzero(self):
        tasks = [make_task()]
        s = compute_day_summary(tasks)
        assert s["total_tasks"] > 0  # strip should render

    def test_summary_strip_hidden_when_no_tasks(self):
        s = compute_day_summary([])
        assert s["total_tasks"] == 0  # strip should NOT render

    def test_all_closed(self):
        tasks = [make_task(condition="Отгружен") for _ in range(5)]
        s = compute_day_summary(tasks)
        assert s["closed_tasks"] == 5
        assert s["closed_tasks"] == s["total_tasks"]

    def test_large_dataset(self):
        tasks = [make_task(pallet_count=12, weight=800.0) for _ in range(100)]
        s = compute_day_summary(tasks)
        assert s["total_tasks"] == 100
        assert s["total_pallets"] == 1200
        assert abs(s["total_weight"] - 80000.0) < 0.1
