"""
transport_sprint32_load_test.py — Load tests for Sprint 32 (Overload warning).

Sprint 32 is purely frontend (overload banner). Load tests are regression
tests for the task+STs endpoints that drive the overload calculation.

NFR:
  - GET /tasks/{id}       p95 ≤ 300ms
  - GET /tasks/{id}/sts   p95 ≤ 300ms
  - GET /vehicles         p95 ≤ 200ms  (vehicle PALLETS needed for bar)

Run:
    locust -f tests/transport/transport_sprint32_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TASK_ID = 1  # adjust to a real task ID in dev DB


class OverloadDataUser(HttpUser):
    wait_time = between(2, 5)

    @task(4)
    def get_task(self):
        self.client.get(
            f"/api/admin/transport/tasks/{TASK_ID}",
            auth=AUTH,
            name="GET /tasks/{id}",
        )

    @task(4)
    def get_task_sts(self):
        self.client.get(
            f"/api/admin/transport/tasks/{TASK_ID}/sts",
            auth=AUTH,
            name="GET /tasks/{id}/sts",
        )

    @task(2)
    def list_vehicles(self):
        self.client.get(
            "/api/admin/transport/vehicles",
            auth=AUTH,
            name="GET /vehicles",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /tasks/{id}":     ("GET", 300),
        "GET /tasks/{id}/sts": ("GET", 300),
        "GET /vehicles":       ("GET", 200),
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
