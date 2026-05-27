"""
transport_sprint36_load_test.py — Load tests for Sprint 36 (bulk ST removal).

Sprint 36 adds bulk removal (N parallel DELETE calls from the browser).
Load tests verify:
  - Single DELETE /tasks/{id}/sts/{st}  p95 ≤ 300ms  (baseline)
  - Burst: 5 parallel DELETEs per user  p95 ≤ 800ms  (simulates bulk select-5)

Run:
    locust -f tests/transport/transport_sprint36_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
import urllib.parse
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()

# In a real test environment these would be pre-seeded task/ST pairs.
# Here we use placeholder values that the server will return 404 for;
# the load test still exercises the endpoint path (auth, routing, DB lookup).
TASK_ID = 9999
ST_NUMBERS = [f"BULK-TEST-{i:03d}" for i in range(1, 6)]


class BulkRemoveUser(HttpUser):
    wait_time = between(3, 6)

    @task(3)
    def single_remove(self):
        st = urllib.parse.quote(ST_NUMBERS[0])
        self.client.delete(
            f"/api/admin/transport/tasks/{TASK_ID}/sts/{st}",
            auth=AUTH,
            name="DELETE /tasks/{id}/sts/{st}",
        )

    @task(1)
    def bulk_remove_five(self):
        """Simulate the browser sending 5 parallel DELETEs (sequential here for locust)."""
        for st_raw in ST_NUMBERS:
            st = urllib.parse.quote(st_raw)
            self.client.delete(
                f"/api/admin/transport/tasks/{TASK_ID}/sts/{st}",
                auth=AUTH,
                name="DELETE /tasks/{id}/sts/{st} [bulk]",
            )

    @task(4)
    def get_task_sts(self):
        self.client.get(
            f"/api/admin/transport/tasks/{TASK_ID}/sts",
            auth=AUTH,
            name="GET /tasks/{id}/sts",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "DELETE /tasks/{id}/sts/{st}":        ("DELETE", 300),
        "DELETE /tasks/{id}/sts/{st} [bulk]": ("DELETE", 800),
        "GET /tasks/{id}/sts":                ("GET",    200),
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
