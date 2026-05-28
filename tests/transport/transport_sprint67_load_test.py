"""Sprint 67 load test — no new endpoints; measures trip detail rendering path."""
from locust import HttpUser, task, between


class Sprint67LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(3)
    def get_task_sts(self):
        self.client.get("/api/admin/transport/task_sts?task_id=1")

    @task(1)
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?date=2026-05-28")
