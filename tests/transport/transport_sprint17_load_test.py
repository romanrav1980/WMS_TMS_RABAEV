"""
transport_sprint17_load_test.py — Load tests for Sprint 17 (billing registry).

NFR targets:
  GET  /billing/orders              p95 ≤ 300 ms
  GET  /billing/orders?date_from=X  p95 ≤ 300 ms
  GET  /billing/orders?company=X    p95 ≤ 300 ms

Run:
    locust -f tests/transport/transport_sprint17_load_test.py \
        --host http://127.0.0.1:8088 --users 8 --spawn-rate 3 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date, timedelta

TODAY = date.today().isoformat()
WEEK_AGO = (date.today() - timedelta(days=7)).isoformat()


class BillingRegistryUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")

    @task(5)
    def list_all_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=self.auth,
            name="GET /billing/orders",
        )

    @task(3)
    def list_orders_by_date(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            params={"date_from": WEEK_AGO, "date_to": TODAY},
            auth=self.auth,
            name="GET /billing/orders?date_from=X",
        )

    @task(2)
    def list_orders_by_company(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            params={"company": "ООО"},
            auth=self.auth,
            name="GET /billing/orders?company=X",
        )

    @task(1)
    def list_orders_paid(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            params={"payed": 1},
            auth=self.auth,
            name="GET /billing/orders?payed=1",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders":             ("GET", 300),
        "GET /billing/orders?date_from=X": ("GET", 300),
        "GET /billing/orders?company=X":   ("GET", 300),
        "GET /billing/orders?payed=1":     ("GET", 300),
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
