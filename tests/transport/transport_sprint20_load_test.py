"""
transport_sprint20_load_test.py — Load tests for Sprint 20 (billing protection).

NFR targets: Same as Sprint 18 — mutations are fast because they 409 early.
  POST /tasks/{id}/cancel (billed) p95 ≤ 200 ms (early 409)
  POST /tasks/{id}/sts   (billed) p95 ≤ 200 ms (early 409)

Run:
    locust -f tests/transport/transport_sprint20_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date

TODAY = date.today().isoformat()


class BillingProtectionUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")
    _billed_task_id: int | None = None

    def on_start(self):
        r = self.client.get(
            "/api/admin/transport/tasks",
            params={"stdate": TODAY},
            auth=self.auth,
        )
        if r.status_code == 200:
            for task in r.json():
                if task.get("PAY_ORDER_ID"):
                    self._billed_task_id = task["ID"]
                    break

    @task(4)
    def cancel_billed_trip(self):
        if not self._billed_task_id:
            return
        self.client.post(
            f"/api/admin/transport/tasks/{self._billed_task_id}/cancel",
            auth=self.auth,
            name="POST /tasks/{id}/cancel (billed)",
        )

    @task(4)
    def assign_st_to_billed(self):
        if not self._billed_task_id:
            return
        self.client.post(
            f"/api/admin/transport/tasks/{self._billed_task_id}/sts",
            json={"st_numbers": ["СТ-LOAD-TEST"]},
            auth=self.auth,
            name="POST /tasks/{id}/sts (billed)",
        )

    @task(2)
    def list_tasks(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"stdate": TODAY},
            auth=self.auth,
            name="GET /tasks",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "POST /tasks/{id}/cancel (billed)": ("POST", 200),
        "POST /tasks/{id}/sts (billed)":    ("POST", 200),
        "GET /tasks":                       ("GET",  300),
    }

    for name, (method, threshold_ms) in targets.items():
        entry = stats.entries.get((name, method))
        if entry and entry.num_requests > 0:
            p95 = entry.get_response_time_percentile(0.95)
            if p95 > threshold_ms:
                failures.append(f"NFR FAIL: {name} p95={p95:.0f}ms > {threshold_ms}ms")

    if failures:
        print("\n".join(failures))
        environment.process_exit_code = 1
