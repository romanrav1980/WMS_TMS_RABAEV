"""
transport_sprint41_load_test.py — Load tests for Sprint 41 (routes status filter).

Status filter is client-side (no new backend calls); the load profile is the
tasks endpoint with the same parameters as the routes tab.
NFR: p95 < 700 ms, error rate < 1 %.
"""

from locust import HttpUser, task, between, events

_nfr_failures: list[str] = []


class RoutesStatusFilterUser(HttpUser):
    wait_time = between(1, 3)
    default_headers = {"Authorization": "Bearer test-token"}

    @task(6)
    def load_routes_default(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (routes tab, all statuses)",
        )

    @task(2)
    def load_routes_date_range(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "date_to": "2026-05-31", "include_readiness": "true"},
            headers=self.default_headers,
            name="/tasks (routes tab, date range)",
        )

    @task(1)
    def load_routes_no_payments(self):
        self.client.get(
            "/api/admin/transport/tasks",
            params={"shipment_date": "2026-05-28", "no_payments_only": "true"},
            headers=self.default_headers,
            name="/tasks (routes, no_payments)",
        )


@events.quitting.add_listener
def check_nfr(environment, **_kw):
    stats = environment.runner.stats
    endpoint = "/tasks (routes tab, all statuses)"
    entry = stats.entries.get((endpoint, "GET"))
    if entry is None:
        print("[NFR] WARNING: no stats for routes endpoint — skipping NFR check")
        return

    p95_ms = entry.get_response_time_percentile(0.95)
    err_rate = entry.fail_ratio * 100

    if p95_ms > 700:
        _nfr_failures.append(f"p95 {p95_ms:.0f} ms > 700 ms threshold")
    if err_rate > 1.0:
        _nfr_failures.append(f"error rate {err_rate:.1f}% > 1% threshold")

    if _nfr_failures:
        print(f"[NFR FAIL] {'; '.join(_nfr_failures)}")
        environment.process_exit_code = 1
    else:
        print(f"[NFR PASS] p95={p95_ms:.0f}ms err={err_rate:.2f}%")
