"""
transport_sprint22_load_test.py — Load tests for Sprint 22 (companies directory + num_plat).

NFR:
  - GET /billing/companies  p95 ≤ 200ms  (simple lookup, cached well)
  - GET /billing/orders     p95 ≤ 300ms  (includes NUM_PLAT in GROUP BY — no regression)

Run:
    locust -f tests/transport/transport_sprint22_load_test.py \
        --host http://127.0.0.1:8088 --users 8 --spawn-rate 3 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")


class BillingCompaniesUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def get_companies(self):
        self.client.get(
            "/api/admin/transport/billing/companies",
            auth=AUTH,
            name="GET /billing/companies",
        )

    @task(5)
    def list_billing_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=AUTH,
            name="GET /billing/orders",
        )

    @task(3)
    def list_billing_filtered(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            params={"closed": 0},
            auth=AUTH,
            name="GET /billing/orders?closed=0",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/companies":   ("GET", 200),
        "GET /billing/orders":      ("GET", 300),
        "GET /billing/orders?closed=0": ("GET", 300),
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
