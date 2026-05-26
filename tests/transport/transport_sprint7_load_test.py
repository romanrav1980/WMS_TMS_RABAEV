"""
transport_sprint7_load_test.py — Load / stress tests for Sprint 7 endpoints.

Endpoints under test:
  GET /api/admin/transport/planner/orders?date=...  (NFR: p95 < 600 ms)
  GET /api/admin/transport/routing/status           (NFR: p95 < 200 ms)

Run (requires locust):
    locust -f tests/transport/transport_sprint7_load_test.py \
           --headless -u 30 -r 5 -t 60s \
           --host http://127.0.0.1:8088 \
           --html test-results/sprint7_load_report.html

Or quick smoke run (10 users, 30 s):
    locust -f tests/transport/transport_sprint7_load_test.py \
           --headless -u 10 -r 2 -t 30s \
           --host http://127.0.0.1:8088 \
           --csv test-results/sprint7
"""
from __future__ import annotations

import base64
import os
import random
from datetime import date, timedelta

from locust import HttpUser, between, task, events

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

AUTH_HEADER = "Basic " + base64.b64encode(
    os.environ.get("TMS_AUTH", "admin:admin123").encode()
).decode()

DATES = [
    (date.today() + timedelta(days=d)).isoformat()
    for d in range(0, 7)
]

TRANSPORT_TYPES = ["", "10", "20", "30"]


# ---------------------------------------------------------------------------
# Locust user
# ---------------------------------------------------------------------------

class PlannerUser(HttpUser):
    wait_time = between(0.3, 1.2)

    def on_start(self):
        self.client.headers.update({
            "Authorization": AUTH_HEADER,
            "Content-Type": "application/json",
        })

    @task(5)
    def get_planner_orders_no_filter(self):
        """Main planner load — date only, no transport_type filter."""
        dt = random.choice(DATES)
        with self.client.get(
            "/api/admin/transport/planner/orders",
            params={"date": dt},
            name="GET /planner/orders (no_filter)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"status={resp.status_code}")
            elif resp.elapsed.total_seconds() > 1.5:
                resp.failure(f"too slow: {resp.elapsed.total_seconds():.3f}s")
            else:
                resp.success()

    @task(3)
    def get_planner_orders_with_type(self):
        """Planner with transport_type filter."""
        dt = random.choice(DATES)
        tt = random.choice(TRANSPORT_TYPES[1:])  # skip empty
        with self.client.get(
            "/api/admin/transport/planner/orders",
            params={"date": dt, "transport_type": tt},
            name="GET /planner/orders (transport_type)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"status={resp.status_code}")
            elif resp.elapsed.total_seconds() > 1.5:
                resp.failure(f"too slow: {resp.elapsed.total_seconds():.3f}s")
            else:
                resp.success()

    @task(2)
    def get_routing_status(self):
        """Routing/geocoding status — should be very fast."""
        with self.client.get(
            "/api/admin/transport/routing/status",
            name="GET /routing/status",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"status={resp.status_code}")
            elif resp.elapsed.total_seconds() > 0.5:
                resp.failure(f"too slow: {resp.elapsed.total_seconds():.3f}s")
            else:
                resp.success()


# ---------------------------------------------------------------------------
# Assertions on test finish (pytest-compatible report hook)
# ---------------------------------------------------------------------------

@events.quitting.add_listener
def assert_nfr(environment, **_kwargs):
    stats = environment.stats
    failures: list[str] = []

    nfr = {
        "GET /planner/orders (no_filter)":    0.600,
        "GET /planner/orders (transport_type)": 0.600,
        "GET /routing/status":               0.200,
    }
    for name, p95_limit in nfr.items():
        entry = stats.get(name, "GET")
        if entry is None or entry.num_requests == 0:
            print(f"[WARN] No requests recorded for: {name}")
            continue
        p95 = entry.get_response_time_percentile(0.95) / 1000.0
        print(f"  {name}: p95={p95:.3f}s (limit {p95_limit}s, n={entry.num_requests})")
        if p95 > p95_limit:
            failures.append(
                f"NFR FAIL {name}: p95={p95:.3f}s > {p95_limit}s"
            )

    if failures:
        print("\n[LOAD TEST] NFR VIOLATIONS:")
        for f in failures:
            print(" ", f)
        environment.process_exit_code = 1
    else:
        print("\n[LOAD TEST] All NFR checks PASSED.")
