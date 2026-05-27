"""
transport_sprint35_load_test.py — Load tests for Sprint 35 (raion filter).

Sprint 35 adds server-side raion filter. Load tests verify the filtered
endpoint is faster than without filter (fewer rows processed).

NFR:
  - GET /available-sts (no filter)      p95 ≤ 400ms
  - GET /available-sts?raion=Север      p95 ≤ 200ms  (filtered, should be faster)
  - POST /clusters/{raion}/create-task  p95 ≤ 1200ms  (improved from Sprint 29 1500ms)

Run:
    locust -f tests/transport/transport_sprint35_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
import urllib.parse
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
TEST_RAION = urllib.parse.quote("Север")


class RaionFilterUser(HttpUser):
    wait_time = between(2, 5)

    @task(4)
    def list_sts_all(self):
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={TODAY}",
            auth=AUTH,
            name="GET /available-sts",
        )

    @task(4)
    def list_sts_raion(self):
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={TODAY}&raion={TEST_RAION}",
            auth=AUTH,
            name="GET /available-sts?raion=",
        )

    @task(2)
    def create_from_cluster(self):
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
        "GET /available-sts":       ("GET",  400),
        "GET /available-sts?raion=": ("GET",  200),
        "POST /clusters/create-task": ("POST", 1200),
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
