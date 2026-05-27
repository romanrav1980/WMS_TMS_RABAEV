"""
transport_sprint18_load_test.py — Load tests for Sprint 18 (price management).

NFR targets:
  POST  /tasks/{id}/recalculate-price p95 ≤ 1000 ms (Oracle function call)
  PATCH /tasks/{id}/price             p95 ≤  300 ms
  DELETE /billing/orders/{id}/tasks/{tt_id} p95 ≤ 300 ms

Run:
    locust -f tests/transport/transport_sprint18_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date

TODAY = date.today().isoformat()


class PriceManagementUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")
    _task_id: int | None = None
    _order_id: int | None = None

    def on_start(self):
        r = self.client.get(
            "/api/admin/transport/tasks",
            params={"stdate": TODAY},
            auth=self.auth,
        )
        if r.status_code == 200 and r.json():
            self._task_id = r.json()[0]["ID"]

        r2 = self.client.post(
            "/api/admin/transport/billing/orders",
            json={"company": "ООО Нагрузка-18", "date_from": TODAY, "date_to": TODAY},
            auth=self.auth,
        )
        if r2.status_code in (200, 201):
            self._order_id = r2.json().get("order_id")

    @task(3)
    def recalculate_price(self):
        if not self._task_id:
            return
        self.client.post(
            f"/api/admin/transport/tasks/{self._task_id}/recalculate-price",
            auth=self.auth,
            name="POST /tasks/{id}/recalculate-price",
        )

    @task(5)
    def set_price(self):
        if not self._task_id:
            return
        self.client.patch(
            f"/api/admin/transport/tasks/{self._task_id}/price",
            json={"price": 10000.0},
            auth=self.auth,
            name="PATCH /tasks/{id}/price",
        )

    @task(2)
    def list_billing_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=self.auth,
            name="GET /billing/orders",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "POST /tasks/{id}/recalculate-price": ("POST", 1000),
        "PATCH /tasks/{id}/price":            ("PATCH",  300),
        "GET /billing/orders":                ("GET",    300),
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
