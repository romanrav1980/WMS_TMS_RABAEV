"""
transport_sprint53_load_test.py — Load test for Sprint 53 (collapsible filter panel).

Pure frontend feature — no new backend endpoints.
We test the /available-sts endpoint with varied filter params (simulating the panel usage).
NFR: p95 < 400 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events
import os


class FilterPanelUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "dispatch_user", "password": "test"},
        )

    @task(5)
    def load_available_sts_no_filter(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}",
            name="/available-sts",
        )

    @task(3)
    def load_available_sts_with_filter(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}&addr_mask=Пермь",
            name="/available-sts?addr_mask=",
        )

    @task(1)
    def load_tasks(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/tasks?date={today}",
            name="/tasks",
        )


@events.quitting.add_listener
def assert_nfr(environment, **kwargs):
    stats = environment.runner.stats.get("/available-sts", "GET")
    if stats and stats.num_requests > 0:
        p95 = stats.get_response_time_percentile(0.95)
        err = stats.num_failures / stats.num_requests
        if p95 > 400:
            environment.process_exit_code = 1
            print(f"FAIL p95={p95:.0f}ms > 400ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
