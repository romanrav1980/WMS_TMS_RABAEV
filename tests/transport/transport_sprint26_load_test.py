"""
transport_sprint26_load_test.py — Load tests for Sprint 26 (Excel export).

Sprint 26 adds GET /billing/orders/{id}/export.xlsx — an Excel export endpoint
backed by openpyxl. Tests verify it meets NFR alongside other billing endpoints.

NFR:
  - GET /billing/orders/{id}/export.xlsx  p95 ≤ 500ms  (file generation, heavier)
  - GET /billing/orders                   p95 ≤ 300ms

Run:
    locust -f tests/transport/transport_sprint26_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

import random
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
SAMPLE_ORDER_IDS: list[int] = []


class BillingExportUser(HttpUser):
    wait_time = between(3, 6)

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

    @task(3)
    def export_order_xlsx(self):
        if not SAMPLE_ORDER_IDS:
            return
        oid = random.choice(SAMPLE_ORDER_IDS)
        self.client.get(
            f"/api/admin/transport/billing/orders/{oid}/export.xlsx",
            auth=AUTH,
            name="GET /billing/orders/{id}/export.xlsx",
        )

    @task(2)
    def get_order_tasks(self):
        if not SAMPLE_ORDER_IDS:
            return
        oid = random.choice(SAMPLE_ORDER_IDS)
        self.client.get(
            f"/api/admin/transport/billing/orders/{oid}/tasks",
            auth=AUTH,
            name="GET /billing/orders/{id}/tasks",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders":                    ("GET", 300),
        "GET /billing/orders/{id}/export.xlsx":   ("GET", 500),
        "GET /billing/orders/{id}/tasks":         ("GET", 300),
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
