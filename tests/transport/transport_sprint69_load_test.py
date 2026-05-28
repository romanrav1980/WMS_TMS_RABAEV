"""Sprint 69 load test — no new endpoints; Delete key is client-side."""
from locust import HttpUser, task, between


class Sprint69LoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.client.post(
            "/api/admin/auth/login",
            json={"username": "admin", "password": "admin"},
        )

    @task(2)
    def unassign_st(self):
        self.client.delete("/api/admin/transport/tasks/1/sts/ST-001")

    @task(1)
    def get_task_sts(self):
        self.client.get("/api/admin/transport/task_sts?task_id=1")
