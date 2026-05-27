"""
transport_sprint34_load_test.py — Load tests for Sprint 34 (cancel_task fix).

Sprint 34 is a backend bug fix. Under load, multiple cancel requests should
not leave STs in an inconsistent state.

NFR:
  - POST /tasks/{id}/cancel   p95 ≤ 500ms

Run:
    locust -f tests/transport/transport_sprint34_load_test.py \
        --host http://127.0.0.1:8088 --users 2 --spawn-rate 1 --run-time 30s --headless
"""

from locust import HttpUser, task, between, events

AUTH = ("admin", "admin123")
TASK_IDS = [101, 102, 103]  # adjust to test task IDs that can be safely cancelled


class CancelTaskUser(HttpUser):
    wait_time = between(5, 10)

    @task(1)
    def cancel_task(self):
        import random
        task_id = random.choice(TASK_IDS)
        self.client.post(
            f"/api/admin/transport/tasks/{task_id}/cancel",
            auth=AUTH,
            name="POST /tasks/{id}/cancel",
        )


@events.quitting.add_listener
def check_nfr(environment, **kwargs):
    stats = environment.runner.stats
    failures = []
    entry = stats.entries.get(("POST /tasks/{id}/cancel", "POST"))
    if entry and entry.num_requests > 0:
        p95 = entry.get_response_time_percentile(0.95)
        if p95 > 500:
            failures.append(f"NFR FAIL: POST /tasks/cancel p95={p95:.0f}ms > 500ms")
    if failures:
        print("\n".join(failures))
        environment.process_exit_code = 1
