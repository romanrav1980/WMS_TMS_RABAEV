"""
transport_sprint23_load_test.py — Load tests for Sprint 23 (billing order detail).

NFR:
  - GET /billing/orders/{id}/tasks  p95 ≤ 300ms

Run:
    locust -f tests/transport/transport_sprint23_load_test.py \
        --host http://127.0.0.1:8088 --users 8 --spawn-rate 3 --run-time 60s --headless
"""

import requests
from locust import HttpUser, task, between, events

BASE = "http://127.0.0.1:8088"
AUTH = ("admin", "admin123")


def _get_sample_order_id() -> int | None:
    try:
        r = requests.get(f"{BASE}/api/admin/transport/billing/orders", auth=AUTH, timeout=5)
        orders = r.json()
        return orders[0]["order_id"] if orders else None
    except Exception:
        return None


_SAMPLE_ORDER_ID = _get_sample_order_id()


class BillingDetailUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def list_orders(self):
        self.client.get(
            "/api/admin/transport/billing/orders",
            auth=AUTH,
            name="GET /billing/orders",
        )

    @task(5)
    def get_order_tasks(self):
        if not _SAMPLE_ORDER_ID:
            return
        self.client.get(
            f"/api/admin/transport/billing/orders/{_SAMPLE_ORDER_ID}/tasks",
            auth=AUTH,
            name="GET /billing/orders/{id}/tasks",
        )

    @task(2)
    def get_companies(self):
        self.client.get(
            "/api/admin/transport/billing/companies",
            auth=AUTH,
            name="GET /billing/companies",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /billing/orders":           ("GET", 300),
        "GET /billing/orders/{id}/tasks": ("GET", 300),
        "GET /billing/companies":         ("GET", 200),
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
