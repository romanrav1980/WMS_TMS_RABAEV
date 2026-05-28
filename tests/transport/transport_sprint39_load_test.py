"""
transport_sprint39_load_test.py — Load tests for Sprint 39 (filter reset).

Sprint 39 is pure frontend — no new endpoints.
Load test verifies the available-sts endpoint remains fast
when called with the full range of filter combinations that the
reset button clears, since this is the primary endpoint affected
by filter state changes.

NFR:
  - GET /available-sts (no filters)          p95 ≤ 400ms
  - GET /available-sts (addr_mask filter)    p95 ≤ 300ms
  - GET /available-sts (type + assembled)    p95 ≤ 300ms

Run:
    locust -f tests/transport/transport_sprint39_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
import urllib.parse
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()


class FilterResetUser(HttpUser):
    wait_time = between(2, 4)

    @task(3)
    def sts_no_filter(self):
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={TODAY}",
            auth=AUTH,
            name="GET /available-sts (no filter)",
        )

    @task(3)
    def sts_addr_filter(self):
        addr = urllib.parse.quote("Пермь")
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={TODAY}&addr_mask={addr}",
            auth=AUTH,
            name="GET /available-sts (addr_mask)",
        )

    @task(2)
    def sts_type_assembled(self):
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={TODAY}&transport_type=10&assembled_only=true",
            auth=AUTH,
            name="GET /available-sts (type+assembled)",
        )

    @task(2)
    def sts_all_unassigned_false(self):
        self.client.get(
            f"/api/admin/transport/available-sts?stdate={TODAY}&unassigned_only=false",
            auth=AUTH,
            name="GET /available-sts (all, no filter)",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /available-sts (no filter)":      ("GET", 400),
        "GET /available-sts (addr_mask)":      ("GET", 300),
        "GET /available-sts (type+assembled)": ("GET", 300),
        "GET /available-sts (all, no filter)": ("GET", 400),
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
