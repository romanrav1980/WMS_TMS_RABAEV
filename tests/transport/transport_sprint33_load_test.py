"""
transport_sprint33_load_test.py — Load tests for Sprint 33 («Кратко» mode).

Sprint 33 is purely frontend. Load tests are regression for the routes
table data endpoint.

NFR:
  - GET /tasks   p95 ≤ 300ms

Run:
    locust -f tests/transport/transport_sprint33_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()


class BriefModeUser(HttpUser):
    wait_time = between(2, 5)

    @task(10)
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
    entry = stats.entries.get(("GET /tasks", "GET"))
    if entry and entry.num_requests > 0:
        p95 = entry.get_response_time_percentile(0.95)
        if p95 > 300:
            failures.append(f"NFR FAIL: GET /tasks p95={p95:.0f}ms > 300ms")
    if failures:
        print("\n".join(failures))
        environment.process_exit_code = 1
