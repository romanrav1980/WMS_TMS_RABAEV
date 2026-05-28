"""Sprint 66 load test — trip detail STs endpoint."""
from locust import HttpUser, task, between


class Sprint66LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(3)
    def get_task_sts(self):
        """Fetch STs for a trip — drives VERIFY_PERC population."""
        self.client.get("/api/admin/transport/task_sts?task_id=1")

    @task(1)
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?date=2026-05-28")
