"""
transport_sprint40_load_test.py — Load tests for Sprint 40 (day summary).

The day summary is computed client-side from the already-loaded tasks list,
so the load profile is identical to the tasks endpoint.
NFR: p95 < 800 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []


class DaySummaryUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(5)
    def load_tasks(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28"},
            headers=self.default_headers,
            name="/tasks (day summary source)",
        )

    @task(2)
    def load_tasks_with_filter(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "unassigned_only": "false"},
            headers=self.default_headers,
            name="/tasks (all, day summary)",
        )

    @task(1)
    def load_available_sts(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": "2026-05-28"},
            headers=self.default_headers,
            name="/available-sts",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    endpoint = "/tasks (day summary source)"
    entry = stats.entries.get((endpoint, "GET"))
    if entry is None:
        print("[NFR] WARNING: no stats for tasks endpoint — skipping NFR check")
        return

    p95_ms = entry.get_response_time_percentile(0.95)
    err_rate = entry.fail_ratio * 100

    if p95_ms > 800:
        _nfr_failures.append(f"p95 {p95_ms:.0f} ms > 800 ms threshold")
    if err_rate > 1.0:
        _nfr_failures.append(f"error rate {err_rate:.1f}% > 1% threshold")

    if _nfr_failures:
        print(f"[NFR FAIL] {'; '.join(_nfr_failures)}")
        environment.process_exit_code = 1
    else:
        print(f"[NFR PASS] p95={p95_ms:.0f}ms err={err_rate:.2f}%")
