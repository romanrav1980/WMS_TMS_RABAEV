"""Sprint 78 load test — localStorage is client-side; no new endpoints."""
from locust import HttpUser, task, between


class Sprint78LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(2)
    def available_sts_unassigned(self):
        self.client.get("/api/admin/transport/available-sts?date=2026-05-28&unassigned_only=true")

    @task(1)
    def available_sts_all(self):
        self.client.get("/api/admin/transport/available-sts?date=2026-05-28")
