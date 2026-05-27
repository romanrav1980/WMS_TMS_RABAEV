"""
transport_sprint29_load_test.py — Load tests for Sprint 29 (Create task from cluster).

Sprint 29 adds POST /clusters/{raion}/create-task.

NFR:
  - GET /clusters             p95 ≤ 300ms
  - POST /clusters/.../create-task  p95 ≤ 1500ms  (creates task + assigns STs)

Run:
    locust -f tests/transport/transport_sprint29_load_test.py \
        --host http://127.0.0.1:8088 --users 3 --spawn-rate 1 --run-time 60s --headless
"""

from datetime import date
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
TEST_RAION = "%D0%A1%D0%B5%D0%B2%D0%B5%D1%80"  # URL-encoded «Север»


class ClusterTaskUser(HttpUser):
    wait_time = between(3, 6)

    @task(8)
    def list_clusters(self):
        self.client.get(
            f"/api/admin/transport/clusters?stdate={TODAY}",
            auth=AUTH,
            name="GET /clusters",
        )

    @task(2)
    def create_task_from_cluster(self):
        self.client.post(
            f"/api/admin/transport/clusters/{TEST_RAION}/create-task",
            json={"stdate": TODAY, "transtype": "10"},
            auth=AUTH,
            name="POST /clusters/create-task",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /clusters":               ("GET",  300),
        "POST /clusters/create-task":  ("POST", 1500),
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
