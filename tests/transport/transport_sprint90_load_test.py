"""Sprint 90 load test — clipboard copy is client-side; STs endpoint tested here."""
from locust import HttpUser, task, between


class Sprint90LoadUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(4)
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?shipment_date=2026-05-28")

    @task(3)
    def get_task_sts(self):
        self.client.get("/api/admin/transport/tasks/1247/sts")

    @task(1)
    def get_available_sts(self):
        self.client.get("/api/admin/transport/available-sts?stdate=2026-05-28")
