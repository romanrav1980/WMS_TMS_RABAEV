"""
transport_sprint56_load_test.py — Load test for Sprint 56 (print route sheet).

Pure frontend HTML generation — no new backend endpoints.
We test /tasks/{id}/sts (data needed for the route sheet) under load.
NFR: p95 < 300 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events


class PrintRouteUser(HttpUser):
    wait_time = between(1.0, 3.0)
    host = "http://localhost:8000"

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "dispatch_user", "password": "test"},
        )

    @task(4)
    def load_task_sts(self):
        self.client.get(
            "/api/admin/transport/tasks/9999/sts",
            name="/tasks/{id}/sts",
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
    def load_available_sts(self):
        from datetime import date
        today = date.today().isoformat()
        self.client.get(
            f"/api/admin/transport/available-sts?date={today}",
            name="/available-sts",
        )


@events.quitting.add_listener
def assert_nfr(environment, **kwargs):
    stats = environment.runner.stats.get("/tasks/{id}/sts", "GET")
    if stats and stats.num_requests > 0:
        p95 = stats.get_response_time_percentile(0.95)
        err = stats.num_failures / stats.num_requests
        if p95 > 300:
            environment.process_exit_code = 1
            print(f"FAIL p95={p95:.0f}ms > 300ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
