"""
transport_sprint8_load_test.py — Load tests for Sprint 8 endpoints.

Endpoints under test:
  POST /api/admin/transport/planner/solve     (NFR: p95 < 60s, single user)
  GET  /api/admin/transport/planner/metrics   (NFR: p95 < 500ms)
  POST /api/admin/transport/distance-matrix/rebuild (NFR: p95 < 30s per call)

Note: /planner/solve is CPU-bound; do NOT run with high concurrency.
Use 2-3 users max — more will starve the solver threads.

Run:
    locust -f tests/transport/transport_sprint8_load_test.py \
           --headless -u 3 -r 1 -t 120s \
           --host http://127.0.0.1:8088 \
           --html test-results/sprint8_load_report.html
"""
from __future__ import annotations

import base64
import os
import random
from datetime import date, timedelta

from locust import HttpUser, between, task, events

AUTH_HEADER = "Basic " + base64.b64encode(
    os.environ.get("TMS_AUTH", "admin:admin123").encode()
).decode()

DATES = [
    (date.today() + timedelta(days=d)).isoformat()
    for d in range(1, 4)
]


class PlannerVrpUser(HttpUser):
    wait_time = between(5, 15)  # long pause — solver is heavy

    def on_start(self):
        self.client.headers.update({
            "Authorization": AUTH_HEADER,
            "Content-Type": "application/json",
        })

    @task(4)
    def get_metrics(self):
        with self.client.get(
            "/api/admin/transport/planner/metrics",
            name="GET /planner/metrics",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"status={resp.status_code}")
            elif resp.elapsed.total_seconds() > 1.0:
                resp.failure(f"too slow: {resp.elapsed.total_seconds():.3f}s")
            else:
                resp.success()

    @task(2)
    def solve_vrp(self):
        dt = random.choice(DATES)
        with self.client.post(
            "/api/admin/transport/planner/solve",
            json={"plan_date": dt, "time_limit_s": 10, "source": "haversine"},
            name="POST /planner/solve",
            catch_response=True,
            timeout=90,
        ) as resp:
            if resp.status_code not in (200, 422):
                resp.failure(f"status={resp.status_code}")
            elif resp.status_code == 200 and resp.elapsed.total_seconds() > 60.0:
                resp.failure(f"too slow: {resp.elapsed.total_seconds():.1f}s")
            else:
                resp.success()

    @task(1)
    def rebuild_matrix(self):
        with self.client.post(
            "/api/admin/transport/distance-matrix/rebuild",
            params={"source": "haversine"},
            name="POST /distance-matrix/rebuild",
            catch_response=True,
            timeout=60,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"status={resp.status_code}")
            elif resp.elapsed.total_seconds() > 30.0:
                resp.failure(f"too slow: {resp.elapsed.total_seconds():.1f}s")
            else:
                resp.success()


@events.quitting.add_listener
def assert_nfr(environment, **_kwargs):
    stats = environment.stats
    nfr = {
        "GET /planner/metrics":              0.500,
        "POST /planner/solve":              60.0,
        "POST /distance-matrix/rebuild":    30.0,
    }
    failures: list[str] = []
    for name, p95_limit in nfr.items():
        entry = stats.get(name, "GET") or stats.get(name, "POST")
        if entry is None or entry.num_requests == 0:
            print(f"[WARN] No requests recorded for: {name}")
            continue
        p95 = entry.get_response_time_percentile(0.95) / 1000.0
        print(f"  {name}: p95={p95:.3f}s (limit {p95_limit}s, n={entry.num_requests})")
        if p95 > p95_limit:
            failures.append(f"NFR FAIL {name}: p95={p95:.3f}s > {p95_limit}s")

    if failures:
        print("\n[LOAD TEST] NFR VIOLATIONS:")
        for f in failures:
            print(" ", f)
        environment.process_exit_code = 1
    else:
        print("\n[LOAD TEST] All NFR checks PASSED.")
