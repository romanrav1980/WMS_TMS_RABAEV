"""
transport_sprint55_load_test.py — Load test for Sprint 55 (all-visible STs totals).

Pure frontend derived values — no new backend endpoints.
We test /available-sts with various filter combinations.
NFR: p95 < 400 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events


class AllVisibleTotalsUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = "http://localhost:8000"

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "dispatch_user", "password": "test"},
        )

    @task(4)
    def load_all_sts(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}",
            name="/available-sts",
        )

    @task(3)
    def load_sts_by_ware(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}&ware_ids=9201",
            name="/available-sts?ware",
        )

    @task(2)
    def load_sts_unassigned(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}&unassigned_only=true",
            name="/available-sts?unassigned",
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
