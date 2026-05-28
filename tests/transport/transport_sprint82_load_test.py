"""Sprint 82 load test — client-side fix and localStorage; no new endpoints."""
from locust import HttpUser, task, between


class Sprint82LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task
    def available_sts(self):
        self.client.get("/api/admin/transport/available-sts?date=2026-05-28")
