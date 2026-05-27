"""
transport_sprint30_load_test.py — Load tests for Sprint 30 (LoadBar, pure frontend sprint).

Sprint 30 is purely a frontend change (LoadBar component). Load tests verify
that existing read endpoints still meet NFR under concurrent load.

NFR:
  - GET /tasks/{id}       p95 ≤ 300ms  (task panel loads vehicle)
  - GET /tasks/{id}/sts   p95 ≤ 300ms  (ST list drives bar value)
  - GET /clusters         p95 ≤ 300ms  (regression)

Run:
    locust -f tests/transport/transport_sprint30_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
TASK_ID = 1  # adjust to a real task ID in dev DB


class LoadBarDataUser(HttpUser):
    wait_time = between(2, 5)

    @task(5)
    def get_task_detail(self):
        self.client.get(
            f"/api/admin/transport/tasks/{TASK_ID}",
            auth=AUTH,
            name="GET /tasks/{id}",
        )

    @task(5)
    def get_task_sts(self):
        self.client.get(
            f"/api/admin/transport/tasks/{TASK_ID}/sts",
            auth=AUTH,
            name="GET /tasks/{id}/sts",
        )

    @task(3)
    def list_clusters(self):
        self.client.get(
            f"/api/admin/transport/clusters?stdate={TODAY}",
            auth=AUTH,
            name="GET /clusters",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /tasks/{id}":     ("GET", 300),
        "GET /tasks/{id}/sts": ("GET", 300),
        "GET /clusters":       ("GET", 300),
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
