"""
transport_sprint11_load_test.py — Load tests for Sprint 11 (ARM operations).

NFR targets:
  POST /tasks/{id}/plan-operations  p95 ≤ 500 ms
  GET  /tasks/{id}/operations       p95 ≤ 200 ms
  PATCH /operations/{op_id}/fact    p95 ≤ 200 ms
  GET /vehicles/gantt               p95 ≤ 300 ms

Run:
    locust -f tests/transport/transport_sprint11_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from locust import HttpUser, task, between, events
from datetime import date, timedelta
import random

TOMORROW = (date.today() + timedelta(days=1)).isoformat()
TODAY = date.today().isoformat()

_created_task_ids: list[int] = []
_op_ids: list[int] = []


class ArmOperationsUser(HttpUser):
    wait_time = between(1, 3)
    auth = ("admin", "admin123")

    def on_start(self):
        # Создать тестовый рейс и запланировать операции
        r = self.client.post(
            "/api/admin/transport/tasks",
            json={"transtype": "Газель", "shipment_date": TOMORROW},
            auth=self.auth,
            name="POST /tasks (setup)",
        )
        if r.status_code in (200, 201):
            tid = r.json().get("task_id")
            if tid:
                _created_task_ids.append(tid)
                ops_r = self.client.post(
                    f"/api/admin/transport/tasks/{tid}/plan-operations",
                    auth=self.auth,
                    name="POST /tasks/{id}/plan-operations (setup)",
                )
                if ops_r.status_code == 200:
                    for op in ops_r.json():
                        _op_ids.append(op["op_id"])

    @task(3)
    def get_operations(self):
        if not _created_task_ids:
            return
        tid = random.choice(_created_task_ids)
        self.client.get(
            f"/api/admin/transport/tasks/{tid}/operations",
            auth=self.auth,
            name="GET /tasks/{id}/operations",
        )

    @task(2)
    def plan_operations(self):
        if not _created_task_ids:
            return
        tid = random.choice(_created_task_ids)
        self.client.post(
            f"/api/admin/transport/tasks/{tid}/plan-operations",
            auth=self.auth,
            name="POST /tasks/{id}/plan-operations",
        )

    @task(2)
    def patch_fact(self):
        if not _op_ids:
            return
        op_id = random.choice(_op_ids)
        self.client.patch(
            f"/api/admin/transport/operations/{op_id}/fact",
            json={"fact_start": "2026-05-27 06:15"},
            auth=self.auth,
            name="PATCH /operations/{id}/fact",
        )

    @task(1)
    def vehicles_gantt(self):
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
        "POST /tasks/{id}/plan-operations": 500,
        "GET /tasks/{id}/operations": 200,
        "PATCH /operations/{id}/fact": 200,
        "GET /vehicles/gantt": 300,
    }

    for name, threshold_ms in targets.items():
        entry = stats.entries.get((name, "POST")) or stats.entries.get((name, "GET")) or stats.entries.get((name, "PATCH"))
        if entry and entry.num_requests > 0:
            p95 = entry.get_response_time_percentile(0.95)
            if p95 > threshold_ms:
                failures.append(f"NFR FAIL: {name} p95={p95:.0f}ms > {threshold_ms}ms")

    if failures:
        print("\n".join(failures))
        environment.process_exit_code = 1
