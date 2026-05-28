"""
transport_sprint46_load_test.py — Load tests for Sprint 46 (day step buttons).

Each step fires loadTasks() + loadAvailableSts() for the new date.
Simulates typical day-browsing pattern: sequential date requests.
NFR: p95 < 700 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []

DATES = ["2026-05-27", "2026-05-28", "2026-05-29", "2026-05-30"]


class DayStepUser(HttpUser):
    wait_time = between(1, 2)
    default_headers = {"Authorization": "Bearer test-token"}
    _date_idx = 0

    def next_date(self) -> str:
        d = DATES[self._date_idx % len(DATES)]
        DayStepUser._date_idx += 1
        return d

    @task(5)
    def load_tasks_stepped_date(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": self.next_date(), "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (day step)",
        )

    @task(3)
    def load_available_sts_stepped_date(self):
        self.client.get(
            "/api/admin/transport/available-sts",
            params={"shipment_date": self.next_date()},
            headers=self.default_headers,
            name="/available-sts (day step)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    checks = [
        ("/tasks (day step)", "GET", 700),
        ("/available-sts (day step)", "GET", 600),
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
        print("[NFR PASS] day-step endpoints within NFR thresholds")
