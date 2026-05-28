"""Sprint 86 load test — CSV export is client-side; no new endpoints."""
from locust import HttpUser, task, between


class Sprint86LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task
    def load_tasks_routes(self):
        self.client.get("/api/admin/transport/tasks?shipment_date=2026-05-28&include_readiness=true")
