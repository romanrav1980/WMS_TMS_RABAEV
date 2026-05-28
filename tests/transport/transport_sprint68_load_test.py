"""Sprint 68 load test — no new endpoints; keyboard shortcut is client-side."""
from locust import HttpUser, task, between


class Sprint68LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(3)
    def assign_sts(self):
        """Simulate Ctrl+Enter → POST assign endpoint."""
        self.client.post(
            "/api/admin/transport/tasks/1/sts",
            json={"st_numbers": []},
        )

    @task(1)
    def list_available_sts(self):
        self.client.get("/api/admin/transport/available-sts?date=2026-05-28")
