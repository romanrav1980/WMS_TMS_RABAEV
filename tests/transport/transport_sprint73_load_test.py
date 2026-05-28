"""Sprint 73 load test — no new endpoints; LOGIST is already in payload."""
from locust import HttpUser, task, between


class Sprint73LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?date=2026-05-28")
