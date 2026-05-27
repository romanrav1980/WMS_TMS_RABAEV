"""
transport_sprint37_load_test.py — Load tests for Sprint 37 (select-all + auto-refresh).

Sprint 37 does not add new endpoints, but auto-refresh means every active
browser tab will poll the same two endpoints every 60 s.

Simulate N concurrent dispatchers each polling every ~60 s:
  - GET /available-sts  (data freshness)
  - GET /tasks          (trips list)
  - GET /clusters       (when in clusters view)

NFR targets (shared with earlier sprints, verified here under concurrent load):
  - GET /available-sts  p95 ≤ 400ms
  - GET /tasks          p95 ≤ 400ms
  - GET /clusters       p95 ≤ 300ms

Run:
    locust -f tests/transport/transport_sprint37_load_test.py \
        --host http://127.0.0.1:8088 --users 10 --spawn-rate 2 --run-time 90s --headless
"""

from datetime import date
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()


class PollingDispatcher(HttpUser):
    """Simulates a dispatcher tab that polls data every ~60 s."""

    wait_time = between(55, 65)

    @task(4)
    def poll_available_sts(self):
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={TODAY}&unassigned_only=true",
            auth=AUTH,
            name="GET /available-sts [auto-refresh]",
        )

    @task(4)
    def poll_tasks(self):
        self.client.get(
            f"/api/admin/transport/tasks?shipment_date={TODAY}&include_readiness=true",
            auth=AUTH,
            name="GET /tasks [auto-refresh]",
        )

    @task(2)
    def poll_clusters(self):
        self.client.get(
            f"/api/admin/transport/clusters?stdate={TODAY}",
            auth=AUTH,
            name="GET /clusters [auto-refresh]",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /available-sts [auto-refresh]": ("GET", 400),
        "GET /tasks [auto-refresh]":         ("GET", 400),
        "GET /clusters [auto-refresh]":      ("GET", 300),
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
