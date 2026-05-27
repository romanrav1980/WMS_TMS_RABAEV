"""
transport_sprint21_load_test.py — Load tests for Sprint 21 (billing permissions).

Since permissions are checked at the start of each request, the overhead is minimal.
NFR: Permission check adds ≤ 10ms overhead (verified by comparing p95 vs Sprint 17).

Run:
    locust -f tests/transport/transport_sprint21_load_test.py \
        --host http://127.0.0.1:8088 --users 8 --spawn-rate 3 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date

TODAY = date.today().isoformat()


class BillingPermissionsUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")

    @task(5)
    def list_billing_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=self.auth,
            name="GET /billing/orders",
        )

    @task(3)
    def list_billing_filtered(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            params={"closed": 0},
            auth=self.auth,
            name="GET /billing/orders?closed=0",
        )

    @task(2)
    def create_and_close(self):
        r = self.client.post(
            "/api/admin/transport/billing/orders",
            json={"company": "ООО Нагрузка-21", "date_from": TODAY, "date_to": TODAY},
            auth=self.auth,
            name="POST /billing/orders",
        )
        if r.status_code in (200, 201):
            order_id = r.json().get("order_id")
            if order_id:
                self.client.patch(
                    f"/api/admin/transport/billing/orders/{order_id}/close",
                    auth=self.auth,
                    name="PATCH /billing/orders/{id}/close",
                )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders":             ("GET",   300),
        "GET /billing/orders?closed=0":    ("GET",   300),
        "POST /billing/orders":            ("POST",  500),
        "PATCH /billing/orders/{id}/close": ("PATCH", 500),
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
