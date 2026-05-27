"""
transport_sprint12_load_test.py — Load tests for Sprint 12 (Gantt diagram).

NFR targets (§12 ТЗ):
  GET /vehicles/gantt (30 vehicles × 15 ops)  p95 ≤ 2000 ms
  GET /tasks/{id}/operations                  p95 ≤  200 ms

Run:
    locust -f tests/transport/transport_sprint12_load_test.py \
        --host http://127.0.0.1:8088 --users 10 --spawn-rate 3 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date, timedelta
import random

TODAY    = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()

_task_ids: list[int] = []


class GanttUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")

    def on_start(self):
        r = self.client.post(
            "/api/admin/transport/tasks",
            json={"transtype": "Газель", "shipment_date": TOMORROW},
            auth=self.auth,
            name="POST /tasks (setup)",
        )
        if r.status_code in (200, 201):
            tid = r.json().get("task_id")
            if tid:
                _task_ids.append(tid)
                self.client.post(
                    f"/api/admin/transport/tasks/{tid}/plan-operations",
                    auth=self.auth,
                    name="POST /tasks/{id}/plan-operations (setup)",
                )

    @task(5)
    def get_gantt_tomorrow(self):
        self.client.get(
            "/api/admin/transport/vehicles/gantt",
            params={"gantt_date": TOMORROW},
            auth=self.auth,
            name="GET /vehicles/gantt",
        )

    @task(3)
    def get_gantt_today(self):
        self.client.get(
            "/api/admin/transport/vehicles/gantt",
            params={"gantt_date": TODAY},
            auth=self.auth,
            name="GET /vehicles/gantt",
        )

    @task(2)
    def get_operations(self):
        if not _task_ids:
            return
        tid = random.choice(_task_ids)
        self.client.get(
            f"/api/admin/transport/tasks/{tid}/operations",
            auth=self.auth,
            name="GET /tasks/{id}/operations",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "GET /vehicles/gantt":          ("GET",   2000),
        "GET /tasks/{id}/operations":   ("GET",    200),
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
