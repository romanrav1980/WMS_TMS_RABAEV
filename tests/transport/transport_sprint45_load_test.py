"""
transport_sprint45_load_test.py — Load tests for Sprint 45 (goto-trip button).

Goto-trip may trigger GET /tasks/{id} when the trip is not in the loaded list.
NFR: GET /tasks/{id} p95 < 400 ms, GET /tasks list p95 < 700 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []

TASK_ID = 1247


class GotoTripUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(5)
    def load_available_sts_unassigned_false(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": "2026-05-28", "unassigned_only": "false"},
            headers=self.default_headers,
            name="/available-sts (all, goto-trip visible)",
        )

    @task(3)
    def get_single_task(self):
        self.client.get(
            f"/api/admin/transport/tasks/{TASK_ID}",
            headers=self.default_headers,
            name="/tasks/{id} (goto-trip fetch)",
        )

    @task(2)
    def load_tasks_list(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (routes tab)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    checks = [
        ("/tasks/{id} (goto-trip fetch)", "GET", 400),
        ("/tasks (routes tab)", "GET", 700),
    ]
    for name, method, threshold_ms in checks:
        entry = stats.entries.get((name, method))
        if entry is None:
            continue
        p95_ms = entry.get_response_time_percentile(0.95)
        err_rate = entry.fail_ratio * 100
        if p95_ms > threshold_ms:
            _nfr_failures.append(f"{name} p95 {p95_ms:.0f}ms > {threshold_ms}ms")
        if err_rate > 1.0:
            _nfr_failures.append(f"{name} err {err_rate:.1f}% > 1%")

    if _nfr_failures:
        print(f"[NFR FAIL] {'; '.join(_nfr_failures)}")
        environment.process_exit_code = 1
    else:
        print("[NFR PASS] goto-trip endpoints within NFR thresholds")
