"""
transport_sprint28_load_test.py — Load tests for Sprint 28 (Tasks Excel export).

Sprint 28 adds GET /tasks/export.xlsx. Tests verify NFR alongside existing endpoints.

NFR:
  - GET /tasks                p95 ≤ 300ms
  - GET /tasks/export.xlsx    p95 ≤ 600ms  (XLSX generation)

Run:
    locust -f tests/transport/transport_sprint28_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()


class TasksExportUser(HttpUser):
    wait_time = between(2, 5)

    @task(6)
    def list_tasks(self):
        self.client.get(
            f"/api/admin/transport/tasks?shipment_date={TODAY}",
            auth=AUTH,
            name="GET /tasks",
        )

    @task(2)
    def export_tasks_xlsx_date(self):
        self.client.get(
            f"/api/admin/transport/tasks/export.xlsx?shipment_date={TODAY}",
            auth=AUTH,
            name="GET /tasks/export.xlsx",
        )

    @task(1)
    def export_tasks_xlsx_all(self):
        self.client.get(
            "/api/admin/transport/tasks/export.xlsx",
            auth=AUTH,
            name="GET /tasks/export.xlsx (all)",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /tasks":                ("GET", 300),
        "GET /tasks/export.xlsx":    ("GET", 600),
        "GET /tasks/export.xlsx (all)": ("GET", 800),
    }

    for name, (method, threshold_ms) in targets.items():
        entry = stats.entries.get((name, method))
        if entry and entry.num_requests > 0:
            p95 = entry.get_response_time_percentile(0.95)
            if p95 > threshold_ms:
                failures.append(f"NFR FAIL: {name} p95={p95:.0f}ms > {threshold_ms}ms")

    if failures:
        print("\n".join(failures))
        environment.process_exit_code = 1
