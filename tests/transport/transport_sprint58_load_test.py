"""
transport_sprint58_load_test.py — Load test for Sprint 58 (expand/collapse all clusters).

Pure frontend state change — no new backend endpoints.
We test the /clusters endpoint used to populate cluster list.
NFR: p95 < 300 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events


class ClusterExpandUser(HttpUser):
    wait_time = between(0.5, 2.0)
    host = "http://localhost:8000"

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "dispatch_user", "password": "test"},
        )

    @task(5)
    def load_clusters(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/clusters?date={today}",
            name="/clusters",
        )

    @task(2)
    def load_available_sts(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}",
            name="/available-sts",
        )


@events.quitting.add_listener
def assert_nfr(environment, **kwargs):
    stats = environment.runner.stats.get("/clusters", "GET")
    if stats and stats.num_requests > 0:
        p95 = stats.get_response_time_percentile(0.95)
        err = stats.num_failures / stats.num_requests
        if p95 > 300:
            environment.process_exit_code = 1
            print(f"FAIL p95={p95:.0f}ms > 300ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
