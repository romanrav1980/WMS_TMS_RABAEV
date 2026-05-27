"""
transport_sprint27_load_test.py — Load tests for Sprint 27 (Registry Excel export).

Sprint 27 adds GET /billing/orders/export.xlsx for full registry export.
This endpoint queries all orders + builds XLSX — heavier than list endpoint.

NFR:
  - GET /billing/orders                p95 ≤ 300ms
  - GET /billing/orders/export.xlsx    p95 ≤ 800ms  (file generation, larger dataset)
  - GET /billing/orders/{id}/export.xlsx p95 ≤ 500ms

Run:
    locust -f tests/transport/transport_sprint27_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

import random
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
SAMPLE_ORDER_IDS: list[int] = []


class BillingRegistryUser(HttpUser):
    wait_time = between(3, 7)

    def on_start(self):
        r = self.client.get(
            "/api/admin/transport/billing/orders",
            auth=AUTH,
            name="GET /billing/orders (setup)",
        )
        if r.status_code == 200:
            SAMPLE_ORDER_IDS.extend(
                o["order_id"] for o in r.json()[:10]
                if o["order_id"] not in SAMPLE_ORDER_IDS
            )

    @task(5)
    def list_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=AUTH,
            name="GET /billing/orders",
        )

    @task(2)
    def export_registry_xlsx(self):
        self.client.get(
            "/api/admin/transport/billing/orders/export.xlsx",
            auth=AUTH,
            name="GET /billing/orders/export.xlsx",
        )

    @task(1)
    def export_order_xlsx(self):
        if not SAMPLE_ORDER_IDS:
            return
        oid = random.choice(SAMPLE_ORDER_IDS)
        self.client.get(
            f"/api/admin/transport/billing/orders/{oid}/export.xlsx",
            auth=AUTH,
            name="GET /billing/orders/{id}/export.xlsx",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders":                    ("GET", 300),
        "GET /billing/orders/export.xlsx":         ("GET", 800),
        "GET /billing/orders/{id}/export.xlsx":   ("GET", 500),
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
