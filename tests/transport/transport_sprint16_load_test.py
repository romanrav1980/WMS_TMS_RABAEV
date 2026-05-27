"""
transport_sprint16_load_test.py — Load tests for Sprint 16 (billing: close/pay).

NFR targets:
  GET  /billing/orders/{id}    p95 ≤ 300 ms
  PATCH /billing/orders/{id}/close p95 ≤ 500 ms
  PATCH /billing/orders/{id}/pay   p95 ≤ 500 ms

Run:
    locust -f tests/transport/transport_sprint16_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date

TODAY = date.today().isoformat()


class BillingStatusUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")
    _order_id: int | None = None

    def on_start(self):
        r = self.client.post(
            "/api/admin/transport/billing/orders",
            json={"company": "ООО Нагрузка-16", "date_from": TODAY, "date_to": TODAY},
            auth=self.auth,
        )
        if r.status_code in (200, 201):
            self._order_id = r.json().get("order_id")

    @task(5)
    def get_order(self):
        if not self._order_id:
            return
        self.client.get(
            f"/api/admin/transport/billing/orders/{self._order_id}",
            auth=self.auth,
            name="GET /billing/orders/{id}",
        )

    @task(2)
    def list_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=self.auth,
            name="GET /billing/orders",
        )

    @task(1)
    def close_then_pay(self):
        if not self._order_id:
            return
        self.client.patch(
            f"/api/admin/transport/billing/orders/{self._order_id}/close",
            auth=self.auth,
            name="PATCH /billing/orders/{id}/close",
        )
        self.client.patch(
            f"/api/admin/transport/billing/orders/{self._order_id}/pay",
            auth=self.auth,
            name="PATCH /billing/orders/{id}/pay",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders/{id}":         ("GET",   300),
        "GET /billing/orders":              ("GET",   300),
        "PATCH /billing/orders/{id}/close": ("PATCH", 500),
        "PATCH /billing/orders/{id}/pay":   ("PATCH", 500),
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
