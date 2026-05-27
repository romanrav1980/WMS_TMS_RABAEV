"""
transport_sprint24_load_test.py — Load tests for Sprint 24 (VRP drag-and-drop).

Sprint 24 is client-side only (no new API endpoints). Tests verify existing
VRP planner endpoints still meet NFR after frontend changes.

NFR:
  - GET /planner/metrics   p95 ≤ 200ms
  - GET /planner/history   p95 ≤ 300ms

Run:
    locust -f tests/transport/transport_sprint24_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")


class PlannerUser(HttpUser):
    wait_time = between(2, 4)

    @task(5)
    def get_metrics(self):
        self.client.get(
            "/api/admin/transport/planner/metrics",
            auth=AUTH,
            name="GET /planner/metrics",
        )

    @task(3)
    def get_history(self):
        self.client.get(
            "/api/admin/transport/planner/history",
            auth=AUTH,
            name="GET /planner/history",
        )

    @task(2)
    def get_routing_status(self):
        self.client.get(
            "/api/admin/transport/routing/status",
            auth=AUTH,
            name="GET /routing/status",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /planner/metrics": ("GET", 200),
        "GET /planner/history": ("GET", 300),
        "GET /routing/status":  ("GET", 200),
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
