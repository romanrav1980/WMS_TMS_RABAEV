"""
transport_sprint63_load_test.py — Load test for Sprint 63 (not-assembled badge).

Pure frontend computation — no new backend endpoints.
We test /available-sts (includes VERIFY_PERC in response).
NFR: p95 < 300 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events


class NotReadyBadgeUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = "http://localhost:8000"

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
            f"/api/admin/transport/available-sts?stdate={today}",
            name="/available-sts",
        )

    @task(2)
    def load_available_sts_assembled(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={today}&assembled_only=true",
            name="/available-sts?assembled",
        )


@events.quitting.add_listener
def assert_nfr(environment, **kwargs):
    stats = environment.runner.stats.get("/available-sts", "GET")
    if stats and stats.num_requests > 0:
        p95 = stats.get_response_time_percentile(0.95)
        err = stats.num_failures / stats.num_requests
        if p95 > 300:
            environment.process_exit_code = 1
            print(f"FAIL p95={p95:.0f}ms > 300ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
