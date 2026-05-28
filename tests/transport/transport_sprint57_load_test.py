"""
transport_sprint57_load_test.py — Load test for Sprint 57 (quick-add ST by number).

Sprint 57 uses the existing POST /tasks/{id}/sts endpoint with a single-element array.
NFR: p95 < 500 ms for assign, p95 < 300 ms for task/sts read, error rate < 1 %.
"""

from locust import HttpUser, task, between, events
import os


class QuickAddStUser(HttpUser):
    wait_time = between(1.0, 3.0)
    host = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")

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
    def quick_assign_st(self):
        self.client.post(
            "/api/admin/transport/tasks/9999/sts",
            json={"st_numbers": ["TEST-001"]},
            name="/tasks/{id}/sts POST",
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
    assign_stats = environment.runner.stats.get("/tasks/{id}/sts POST", "POST")
    if assign_stats and assign_stats.num_requests > 0:
        p95 = assign_stats.get_response_time_percentile(0.95)
        err = assign_stats.num_failures / assign_stats.num_requests
        if p95 > 500:
            environment.process_exit_code = 1
            print(f"FAIL assign p95={p95:.0f}ms > 500ms")
        if err > 0.01:
            environment.process_exit_code = 1
            print(f"FAIL error_rate={err:.1%} > 1%")
