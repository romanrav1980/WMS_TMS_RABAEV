"""
transport_sprint31_load_test.py — Load tests for Sprint 31 (Cluster sidebar).

Sprint 31 is purely a frontend change (ClusterSidebar). Load tests are
regression tests for the cluster data endpoint that feeds the sidebar.

NFR:
  - GET /clusters   p95 ≤ 300ms  (feeds sidebar cards)
  - GET /tasks      p95 ≤ 300ms  (main table regression)

Run:
    locust -f tests/transport/transport_sprint31_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()


class ClusterSidebarUser(HttpUser):
    wait_time = between(2, 4)

    @task(6)
    def list_clusters(self):
        self.client.get(
            f"/api/admin/transport/clusters?stdate={TODAY}",
            auth=AUTH,
            name="GET /clusters",
        )

    @task(4)
    def list_tasks(self):
        self.client.get(
            f"/api/admin/transport/tasks?shipment_date={TODAY}",
            auth=AUTH,
            name="GET /tasks",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /clusters": ("GET", 300),
        "GET /tasks":    ("GET", 300),
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
