"""
transport_sprint15_load_test.py — Load tests for Sprint 15 (billing: create order).

NFR targets:
  GET  /billing/orders    p95 ≤  300 ms
  POST /billing/orders    p95 ≤  500 ms
  GET  /tasks/{id}/billing p95 ≤  300 ms

Run:
    locust -f tests/transport/transport_sprint15_load_test.py \
        --host http://127.0.0.1:8088 --users 8 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date

TODAY = date.today().isoformat()


class BillingUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")

    @task(5)
    def list_billing_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=self.auth,
            name="GET /billing/orders",
        )

    @task(2)
    def list_billing_orders_filtered(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            params={"closed": 0},
            auth=self.auth,
            name="GET /billing/orders (filtered)",
        )

    @task(3)
    def create_billing_order(self):
        self.client.post(
            "/api/admin/transport/billing/orders",
            json={"company": "ООО Нагрузка-Тест", "date_from": TODAY, "date_to": TODAY},
            auth=self.auth,
            name="POST /billing/orders",
        )

    @task(2)
    def get_task_billing(self):
        self.client.get(
            "/api/admin/transport/tasks/9999/billing",
            auth=self.auth,
            name="GET /tasks/{id}/billing",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders":          ("GET",  300),
        "GET /billing/orders (filtered)": ("GET", 300),
        "POST /billing/orders":         ("POST", 500),
        "GET /tasks/{id}/billing":      ("GET",  300),
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
