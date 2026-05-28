"""
transport_sprint59_load_test.py — Load test for Sprint 59 (route search).

Pure frontend filter — no new backend endpoints.
We test /tasks endpoint (data loaded before search).
NFR: p95 < 300 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events
import os


class RouteSearchUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "dispatch_user", "password": "test"},
        )

    @task(5)
    def load_tasks(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/tasks?date={today}",
            name="/tasks",
        )

    @task(2)
    def load_tasks_filtered(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/tasks?date={today}&transport=Е715",
            name="/tasks?transport=",
        )


@events.quitting.add_listener
def assert_nfr(environment, **kwargs):
    stats = environment.runner.stats.get("/tasks", "GET")
    if stats and stats.num_requests > 0:
        p95 = stats.get_response_time_percentile(0.95)
        err = stats.num_failures / stats.num_requests
        if p95 > 300:
            environment.process_exit_code = 1
            print(f"FAIL p95={p95:.0f}ms > 300ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
