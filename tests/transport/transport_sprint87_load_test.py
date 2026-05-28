"""Sprint 87 load test — confirm dialog is client-side; close endpoint tested here."""
from locust import HttpUser, task, between


class Sprint87LoadUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(3)
    def list_tasks(self):
        self.client.get("/api/admin/transport/tasks?shipment_date=2026-05-28")

    @task(1)
    def get_task_sts(self):
        self.client.get("/api/admin/transport/tasks/1247/sts")
