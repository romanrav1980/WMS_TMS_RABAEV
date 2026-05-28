"""Sprint 79 load test — TK_NAME already in payload; no new endpoints."""
from locust import HttpUser, task, between


class Sprint79LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?date=2026-05-28")
