"""Sprint 71 load test — CSS-only change; no new endpoints."""
from locust import HttpUser, task, between


class Sprint71LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?date=2026-05-28")
