"""
transport_sprint38_load_test.py — Load tests for Sprint 38 (copy trip).

Sprint 38 adds copy-trip = POST /tasks + PATCH /tasks/{id}.
No new endpoints; we verify both remain fast under load.

NFR:
  - POST /tasks          p95 ≤ 500ms
  - PATCH /tasks/{id}    p95 ≤ 300ms
  - GET  /tasks/{id}     p95 ≤ 200ms   (fetch new task after creation)

Run:
    locust -f tests/transport/transport_sprint38_load_test.py \
        --host http://127.0.0.1:8088 --users 5 --spawn-rate 2 --run-time 60s --headless
"""

from datetime import date
from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
PATCH_TASK_ID = 9999  # placeholder — real env uses a live task id


class CopyTripUser(HttpUser):
    wait_time = between(3, 6)

    @task(3)
    def create_task(self):
        self.client.post(
            "/api/admin/transport/tasks",
            json={"transtype": "10", "shipment_date": TODAY},
            auth=AUTH,
            name="POST /tasks",
        )

    @task(2)
    def patch_task(self):
        self.client.patch(
            f"/api/admin/transport/tasks/{PATCH_TASK_ID}",
            json={"transport": "Е715ТТ"},
            auth=AUTH,
            name="PATCH /tasks/{id}",
        )

    @task(5)
    def get_task(self):
        self.client.get(
            f"/api/admin/transport/tasks/{PATCH_TASK_ID}",
            auth=AUTH,
            name="GET /tasks/{id}",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []

    targets = {
        "POST /tasks":      ("POST",  500),
        "PATCH /tasks/{id}": ("PATCH", 300),
        "GET /tasks/{id}":  ("GET",   200),
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
