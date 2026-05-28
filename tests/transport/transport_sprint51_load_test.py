"""
transport_sprint51_load_test.py — Load test for Sprint 51 (sticky selection bar).

The bar itself is pure frontend state — no new backend endpoints.
We test the existing /available-sts endpoint at selection-time load.
NFR: p95 < 500 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events
import os


class SelectionBarUser(HttpUser):
    wait_time = between(0.5, 1.5)
    host = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "dispatch_user", "password": "test"},
        )

    @task(5)
    def load_available_sts(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}",
            name="/available-sts",
        )

    @task(2)
    def load_tasks(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/tasks?date={today}",
            name="/tasks",
        )

    @task(1)
    def simulate_assign(self):
        """Simulate adding selected STs to a trip (selection bar «Добавить в #ID» button)."""
        self.client.post(
            "/api/admin/transport/tasks/9999/add-sts",
            json={"st_numbers": [1001, 1002, 1003]},
            name="/tasks/{id}/add-sts",
        )


@events.quitting.add_listener
def assert_nfr(environment, **kwargs):
    stats = environment.runner.stats.get("/available-sts", "GET")
    if stats and stats.num_requests > 0:
        p95 = stats.get_response_time_percentile(0.95)
        err = stats.num_failures / stats.num_requests
        if p95 > 500:
            environment.process_exit_code = 1
            print(f"FAIL p95={p95:.0f}ms > 500ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
