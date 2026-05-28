"""Sprint 88 load test — reschedule PATCH endpoint."""
from locust import HttpUser, task, between


class Sprint88LoadUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(5)
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?shipment_date=2026-05-28")

    @task(1)
    def reschedule_task(self):
        self.client.patch(
            "/api/admin/transport/tasks/1247",
            json={"shipment_date": "2026-05-29"},
        )
