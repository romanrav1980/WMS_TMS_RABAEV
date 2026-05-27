"""
transport_sprint19_load_test.py — Load tests for Sprint 19 (link to existing order).

NFR targets:
  GET /billing/orders?company=X&closed=0  p95 ≤ 300 ms
  POST /billing/orders/{id}/tasks         p95 ≤ 500 ms

Run:
    locust -f tests/transport/transport_sprint19_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date

TODAY = date.today().isoformat()


class BillingLinkUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")
    _order_id: int | None = None
    _task_id: int | None = None

    def on_start(self):
        r = self.client.post(
            "/api/admin/transport/billing/orders",
            json={"company": "ООО Нагрузка-19", "date_from": TODAY, "date_to": TODAY},
            auth=self.auth,
        )
        if r.status_code in (200, 201):
            self._order_id = r.json().get("order_id")

        r2 = self.client.get(
            "/api/admin/transport/tasks",
            params={"stdate": TODAY},
            auth=self.auth,
        )
        if r2.status_code == 200 and r2.json():
            for t in r2.json():
                if not t.get("PAY_ORDER_ID"):
                    self._task_id = t["ID"]
                    break

    @task(6)
    def list_open_orders_for_company(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            params={"company": "ООО", "closed": 0, "payed": 0},
            auth=self.auth,
            name="GET /billing/orders?company=X&closed=0",
        )

    @task(2)
    def add_task_to_order(self):
        if not self._order_id or not self._task_id:
            return
        self.client.post(
            f"/api/admin/transport/billing/orders/{self._order_id}/tasks",
            json={"tt_ids": [self._task_id]},
            auth=self.auth,
            name="POST /billing/orders/{id}/tasks",
        )

    @task(2)
    def get_order_tasks(self):
        if not self._order_id:
            return
        self.client.get(
            f"/api/admin/transport/billing/orders/{self._order_id}/tasks",
            auth=self.auth,
            name="GET /billing/orders/{id}/tasks",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders?company=X&closed=0": ("GET",  300),
        "POST /billing/orders/{id}/tasks":        ("POST", 500),
        "GET /billing/orders/{id}/tasks":         ("GET",  300),
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
