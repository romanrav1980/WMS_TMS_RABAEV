"""
transport_sprint94_load_test.py — Load test for Sprint 94 (amber border for unready trips).

Feature is pure frontend CSS — no new backend endpoints.
We test /tasks?include_readiness=true which is the endpoint that provides READY_PERC.
NFR: p95 < 400 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events
import os


class UnreadyTripsUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "dispatch_user", "password": "test"},
        )

    @task(6)
    def load_tasks_with_readiness(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/tasks?shipment_date={today}&include_readiness=true",
            name="/tasks?include_readiness",
        )

    @task(3)
    def load_available_sts(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}",
            name="/available-sts",
        )


@events.quitting.add_listener
def assert_nfr(environment, **kwargs):
    stats = environment.runner.stats.get("/tasks?include_readiness", "GET")
    if stats and stats.num_requests > 0:
        p95 = stats.get_response_time_percentile(0.95)
        err = stats.num_failures / stats.num_requests
        if p95 > 400:
            environment.process_exit_code = 1
            print(f"FAIL p95={p95:.0f}ms > 400ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
