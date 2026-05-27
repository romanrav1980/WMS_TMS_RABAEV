"""
transport_sprint14_load_test.py — Load tests for Sprint 14 (plan-fact analytics).

NFR targets:
  GET /plan-fact (30 days)  p95 ≤ 2000 ms
  GET /plan-fact (1 day)    p95 ≤  500 ms

Run:
    locust -f tests/transport/transport_sprint14_load_test.py \
        --host http://127.0.0.1:8088 --users 10 --spawn-rate 3 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date, timedelta

TODAY    = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()
LAST_30  = (date.today() - timedelta(days=30)).isoformat()


class PlanFactUser(HttpUser):
    wait_time = between(1, 2)
    auth = ("admin", "admin123")

    @task(4)
    def get_plan_fact_day(self):
        self.client.get(
            "/api/admin/transport/plan-fact",
            params={"date_from": TODAY, "date_to": TODAY},
            auth=self.auth,
            name="GET /plan-fact (1 day)",
        )

    @task(2)
    def get_plan_fact_month(self):
        self.client.get(
            "/api/admin/transport/plan-fact",
            params={"date_from": LAST_30, "date_to": TODAY},
            auth=self.auth,
            name="GET /plan-fact (30 days)",
        )

    @task(4)
    def get_gantt(self):
        self.client.get(
            "/api/admin/transport/vehicles/gantt",
            params={"gantt_date": TOMORROW},
            auth=self.auth,
            name="GET /vehicles/gantt",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /plan-fact (1 day)":  ("GET",  500),
        "GET /plan-fact (30 days)": ("GET", 2000),
        "GET /vehicles/gantt":      ("GET", 2000),
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
