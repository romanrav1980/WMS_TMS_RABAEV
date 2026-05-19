from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from threading import Lock
from typing import Any

import oracledb


DEFAULT_BASE_URL = "http://127.0.0.1:8088"
ROOT_DIR = Path(__file__).resolve().parents[3]
WAVE_SCRIPT = ROOT_DIR / "tests" / "load" / "wave" / "wave_replenishment_load_test.py"
RAW_SCRIPT = ROOT_DIR / "tests" / "smoke" / "mes_raw_supply_smoke.py"
FG_SCRIPT = ROOT_DIR / "tests" / "smoke" / "mes_http_workflow.py"


@dataclass
class RequestMetric:
    endpoint: str
    method: str
    status_code: int
    elapsed_ms: float
    ok: bool
    error: str | None = None
    body: str | None = None


@dataclass
class MixedState:
    metrics: list[RequestMetric] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock)

    def add_metric(self, metric: RequestMetric) -> None:
        with self.lock:
            self.metrics.append(metric)


class ApiClient:
    def __init__(self, base_url: str, username: str, password: str, state: MixedState) -> None:
        self.base_url = base_url.rstrip("/")
        token = base64.b64encode(f"{username}:{password}".encode("ascii")).decode("ascii")
        self.headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }
        self.state = state

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        expected_statuses: set[int] | None = None,
        metric_endpoint: str | None = None,
    ) -> tuple[int, Any]:
        expected_statuses = expected_statuses or {200}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(f"{self.base_url}{path}", data=body, method=method, headers=self.headers)
        started = time.perf_counter()
        status_code = 0
        response_body = ""
        error_text = None
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                status_code = response.status
                response_body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            response_body = exc.read().decode("utf-8", errors="replace")
            error_text = response_body[:1000]
        except Exception as exc:  # noqa: BLE001 - load runner must report transport failures.
            error_text = str(exc)
        elapsed_ms = (time.perf_counter() - started) * 1000
        ok = status_code in expected_statuses and not error_text
        self.state.add_metric(
            RequestMetric(
                endpoint=metric_endpoint or f"{method} {path.split('?', 1)[0]}",
                method=method,
                status_code=status_code,
                elapsed_ms=elapsed_ms,
                ok=ok,
                error=None if ok else error_text,
                body=None if ok else response_body[:1000],
            )
        )
        if not ok:
            raise RuntimeError(f"{method} {path} failed with {status_code}: {error_text or response_body[:300]}")
        if not response_body:
            return status_code, None
        try:
            return status_code, json.loads(response_body)
        except json.JSONDecodeError:
            return status_code, response_body

    def get(self, path: str, metric_endpoint: str | None = None) -> Any:
        return self.request("GET", path, metric_endpoint=metric_endpoint)[1]

    def post(self, path: str, payload: dict[str, Any], metric_endpoint: str | None = None) -> Any:
        return self.request("POST", path, payload=payload, metric_endpoint=metric_endpoint)[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mixed warehouse dispatcher/domain-sync load test.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--wave-count", type=int, default=2)
    parser.add_argument("--orders-per-wave", type=int, default=1)
    parser.add_argument("--raw-orders", type=int, default=2)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--cleanup-wave", action="store_true")
    parser.add_argument("--report", default="tests/load/warehouse_tasks/mixed_dispatcher_sync_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = MixedState()
    client = ApiClient(args.base_url, args.username, args.password, state)
    wait_for_api(client)
    baseline_sync_id = max_sync_id()
    started = time.perf_counter()

    jobs = [
        (
            "wave_replenishment",
            [
                sys.executable,
                str(WAVE_SCRIPT),
                "--base-url",
                args.base_url,
                "--username",
                args.username,
                "--password",
                args.password,
                "--waves",
                str(args.wave_count),
                "--orders-per-wave",
                str(args.orders_per_wave),
                "--concurrency",
                str(max(1, min(args.workers, args.wave_count))),
                "--execute-tasks",
            ],
        ),
        (
            "raw_supply",
            [
                sys.executable,
                str(RAW_SCRIPT),
                "--base-url",
                args.base_url,
                "--user",
                args.username,
                "--password",
                args.password,
                "--orders",
                str(args.raw_orders),
                "--workers",
                str(max(1, min(args.workers, args.raw_orders))),
            ],
        ),
        (
            "fg_storage",
            [
                sys.executable,
                str(FG_SCRIPT),
                "--base-url",
                args.base_url,
                "--user",
                args.username,
                "--password",
                args.password,
            ],
        ),
    ]

    job_results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(args.workers, 1)) as pool:
        futures = {pool.submit(run_job, name, command): name for name, command in jobs}
        for future in as_completed(futures):
            name = futures[future]
            job_results[name] = future.result()

    diagnostics = collect_sync_diagnostics(baseline_sync_id)
    retry_result = retry_latest_synced_task(client, baseline_sync_id)
    diagnostics_after_retry = collect_sync_diagnostics(baseline_sync_id)
    assert_mixed_diagnostics(diagnostics, diagnostics_after_retry, retry_result)
    elapsed_s = time.perf_counter() - started
    report = {
        "status": "ok",
        "elapsed_s": round(elapsed_s, 3),
        "baseline_sync_id": baseline_sync_id,
        "jobs": job_results,
        "diagnostics": diagnostics,
        "retry_result": retry_result,
        "diagnostics_after_retry": diagnostics_after_retry,
        "api_metrics": build_metrics(state),
    }
    report_path = ROOT_DIR / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.cleanup_wave:
        cleanup_wave_load_data()


def wait_for_api(client: ApiClient) -> None:
    for _ in range(30):
        try:
            client.get("/health", metric_endpoint="GET /health")
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("API did not become healthy.")


def run_job(name: str, command: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT_DIR,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed_s = time.perf_counter() - started
    if completed.returncode != 0:
        raise RuntimeError(
            f"{name} failed with exit code {completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return {
        "elapsed_s": round(elapsed_s, 3),
        "summary": parse_last_json(completed.stdout),
        "stderr": completed.stderr.strip(),
    }


def parse_last_json(text: str) -> Any:
    decoder = json.JSONDecoder()
    parsed = None
    index = 0
    while index < len(text):
        brace_positions = [pos for pos in (text.find("{", index), text.find("[", index)) if pos >= 0]
        if not brace_positions:
            break
        start = min(brace_positions)
        try:
            value, end = decoder.raw_decode(text[start:])
            parsed = value
            index = start + end
        except json.JSONDecodeError:
            index = start + 1
    return parsed if parsed is not None else text.strip()


def retry_latest_synced_task(client: ApiClient, baseline_sync_id: int) -> dict[str, Any]:
    rows = fetch_all(
        """
        select TASK_ID, SYNC_ID, TASK_SOURCE, TASK_TYPE
          from (
            select TASK_ID, SYNC_ID, TASK_SOURCE, TASK_TYPE
              from RRL_WAREHOUSE_TASK_SYNC
             where SYNC_ID > :baseline_sync_id
               and SYNC_STATUS = 'SYNCED'
             order by SYNC_ID desc
          )
         where rownum = 1
        """,
        {"baseline_sync_id": baseline_sync_id},
    )
    if not rows:
        raise AssertionError("No synced task was found for retry idempotency check.")
    row = rows[0]
    response = client.post(
        f"/api/warehouse-tasks/{row['task_id']}/sync/retry",
        {"updated_by": "mixed-dispatcher-load"},
        metric_endpoint="POST /api/warehouse-tasks/{id}/sync/retry",
    )
    return {"selected": row, "response": response}


def collect_sync_diagnostics(baseline_sync_id: int) -> dict[str, Any]:
    status_rows = fetch_all(
        """
        select SYNC_STATUS, count(*) CNT
          from RRL_WAREHOUSE_TASK_SYNC
         where SYNC_ID > :baseline_sync_id
         group by SYNC_STATUS
        """,
        {"baseline_sync_id": baseline_sync_id},
    )
    source_rows = fetch_all(
        """
        select TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE, SYNC_STATUS, count(*) CNT
          from RRL_WAREHOUSE_TASK_SYNC
         where SYNC_ID > :baseline_sync_id
         group by TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE, SYNC_STATUS
         order by TASK_SOURCE, TASK_TYPE, SOURCE_DOC_TYPE, SYNC_STATUS
        """,
        {"baseline_sync_id": baseline_sync_id},
    )
    duplicate_rows = fetch_all(
        """
        select SYNC_KEY, count(*) CNT
          from RRL_WAREHOUSE_TASK_SYNC
         group by SYNC_KEY
        having count(*) > 1
        """,
        {},
    )
    invalid_rows = fetch_all("select count(*) CNT from USER_OBJECTS where STATUS <> 'VALID'", {})
    return {
        "sync_rows": sum(int(row["cnt"]) for row in status_rows),
        "status_counts": {row["sync_status"]: int(row["cnt"]) for row in status_rows},
        "source_status_counts": source_rows,
        "duplicate_sync_keys": len(duplicate_rows),
        "invalid_objects": int(invalid_rows[0]["cnt"]) if invalid_rows else 0,
    }


def assert_mixed_diagnostics(
    diagnostics: dict[str, Any],
    diagnostics_after_retry: dict[str, Any],
    retry_result: dict[str, Any],
) -> None:
    source_keys = {
        (row["task_source"], row["task_type"], row["source_doc_type"])
        for row in diagnostics["source_status_counts"]
    }
    required = {
        ("WAVE", "REPLENISHMENT", "PICK_WAVE"),
        ("MES_RAW_SUPPLY", "RAW_TO_PRODUCTION", "PRODUCTION_ORDER"),
        ("MES_COMPLETION", "FG_TO_STORAGE", "PRODUCTION_ORDER"),
    }
    missing = required - source_keys
    if missing:
        raise AssertionError(f"Mixed test did not create all required sync sources: {sorted(missing)}")
    if diagnostics["status_counts"].get("ERROR", 0) != 0:
        raise AssertionError(f"Domain sync errors detected: {diagnostics['status_counts']}")
    if diagnostics_after_retry["status_counts"].get("ERROR", 0) != 0:
        raise AssertionError(f"Domain sync errors detected after retry: {diagnostics_after_retry['status_counts']}")
    if diagnostics["duplicate_sync_keys"] != 0 or diagnostics_after_retry["duplicate_sync_keys"] != 0:
        raise AssertionError("Duplicate RRL_WAREHOUSE_TASK_SYNC.SYNC_KEY detected.")
    if diagnostics["invalid_objects"] != 0 or diagnostics_after_retry["invalid_objects"] != 0:
        raise AssertionError("Oracle invalid objects detected.")
    if retry_result["response"].get("sync", {}).get("sync_status") != "SYNCED":
        raise AssertionError(f"Retry idempotency check did not return SYNCED: {retry_result}")


def build_metrics(state: MixedState) -> dict[str, Any]:
    failed = [metric for metric in state.metrics if not metric.ok]
    by_endpoint = {}
    for endpoint in sorted({metric.endpoint for metric in state.metrics}):
        values = [metric.elapsed_ms for metric in state.metrics if metric.endpoint == endpoint]
        by_endpoint[endpoint] = summarize(values)
    return {
        "request_count": len(state.metrics),
        "failed_request_count": len(failed),
        "latency_ms": by_endpoint,
        "errors": [metric.__dict__ for metric in failed[:10]],
    }


def summarize(values: list[float]) -> dict[str, float | int]:
    values = sorted(values)
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "min": round(values[0], 2),
        "p50": round(median(values), 2),
        "p95": round(percentile(values, 95), 2),
        "max": round(values[-1], 2),
    }


def percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0
    index = min(len(values) - 1, max(0, int(round((pct / 100) * (len(values) - 1)))))
    return values[index]


def max_sync_id() -> int:
    rows = fetch_all("select nvl(max(SYNC_ID), 0) SYNC_ID from RRL_WAREHOUSE_TASK_SYNC", {})
    return int(rows[0]["sync_id"]) if rows else 0


def fetch_all(sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        columns = [column[0].lower() for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def connect() -> oracledb.Connection:
    return oracledb.connect(
        user=os.getenv("WMS_ORACLE_USER", "RABAEV"),
        password=os.getenv("WMS_ORACLE_PASSWORD", "RABAEVWMS"),
        dsn=os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"),
    )


def cleanup_wave_load_data() -> None:
    spec = importlib.util.spec_from_file_location("wave_replenishment_load_test", WAVE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load wave cleanup module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.cleanup_load_data()


if __name__ == "__main__":
    main()
