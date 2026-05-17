from __future__ import annotations

import argparse
import base64
import json
import os
import random
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from threading import Lock
from typing import Any

try:
    import oracledb
except ImportError:  # pragma: no cover - reported at runtime when cleanup is requested.
    oracledb = None


LOAD_PREFIX = "LOAD-BOM"
DEFAULT_BASE_URL = "http://127.0.0.1:8088"


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
class LoadState:
    run_prefix: str
    metrics: list[RequestMetric] = field(default_factory=list)
    created_bom_ids: list[int] = field(default_factory=list)
    approved_primary: dict[str, int] = field(default_factory=dict)
    lock: Lock = field(default_factory=Lock)
    expected_conflicts: int = 0

    def add_metric(self, metric: RequestMetric) -> None:
        with self.lock:
            self.metrics.append(metric)

    def add_bom_id(self, bom_id: int) -> None:
        with self.lock:
            self.created_bom_ids.append(bom_id)

    def add_primary(self, product: str, bom_id: int) -> None:
        with self.lock:
            self.approved_primary[product] = bom_id

    def add_expected_conflict(self) -> None:
        with self.lock:
            self.expected_conflicts += 1


class BomLoadClient:
    def __init__(self, base_url: str, username: str, password: str, state: LoadState) -> None:
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
        endpoint = metric_endpoint or normalize_endpoint(method, path)
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(url, data=body, method=method, headers=self.headers)
        started = time.perf_counter()
        status_code = 0
        response_body = ""
        error_text = None
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                status_code = response.status
                response_body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            response_body = exc.read().decode("utf-8", errors="replace")
            error_text = response_body[:1000]
        except Exception as exc:  # noqa: BLE001 - load runner must report any transport failure.
            error_text = str(exc)
        elapsed_ms = (time.perf_counter() - started) * 1000
        ok = status_code in expected_statuses and not error_text
        if status_code in expected_statuses and status_code >= 400:
            ok = True
        self.state.add_metric(
            RequestMetric(
                endpoint=endpoint,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BOM load test for WMS/MES API")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--products", type=int, default=20)
    parser.add_argument("--boms-per-product", type=int, default=5)
    parser.add_argument("--lines-per-bom", type=int, default=25)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--calculate-requests", type=int, default=1000)
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--keep-data", action="store_true")
    parser.add_argument("--report", default="tests/load/bom/report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + random_suffix(5)
    state = LoadState(run_prefix=f"{LOAD_PREFIX}-{run_id}")
    client = BomLoadClient(args.base_url, args.username, args.password, state)
    started_at = utc_now()
    report: dict[str, Any] | None = None

    try:
        ensure_backend_ready(args.base_url, repo_root)
        ensure_bom_openapi(args.base_url)
        if args.cleanup:
            cleanup_load_data()

        product_token = random_suffix(5)
        products = [
            (f"L{product_token}P{idx:04d}" + ("X" * 40))[:40]
            for idx in range(1, args.products + 1)
        ]
        create_bom_load(client, state, products, args.boms_per_product, args.lines_per_bom, args.concurrency)
        conflict_test(client, state)
        concurrent_calculate(client, state, args.calculate_requests, args.concurrency)
        default_lookup(client, state, products, args.concurrency)
        list_and_detail_reads(client, state, args.concurrency)

        finished_at = utc_now()
        report = build_report(state, started_at, finished_at, args)
        write_report(report, repo_root / args.report)
        print(json.dumps(report_summary(report), ensure_ascii=False, indent=2))
        return 0 if report["failed_requests"] == 0 else 1
    finally:
        if args.cleanup and not args.keep_data:
            try:
                cleanup_load_data()
                remaining = count_load_rows()
                print(json.dumps({"cleanup": "done", "remaining_load_bom_rows": remaining}, ensure_ascii=False))
            except Exception as exc:  # noqa: BLE001
                print(f"Cleanup failed: {exc}", file=sys.stderr)
                if report is None:
                    raise


def ensure_backend_ready(base_url: str, repo_root: Path) -> None:
    if endpoint_ok(f"{base_url.rstrip('/')}/health"):
        return
    print("Backend is not responding. Starting serv.bat...")
    creationflags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    subprocess.Popen(["cmd.exe", "/c", "serv.bat"], cwd=repo_root, creationflags=creationflags)
    deadline = time.time() + 45
    while time.time() < deadline:
        if endpoint_ok(f"{base_url.rstrip('/')}/health"):
            return
        time.sleep(1)
    raise RuntimeError(f"Backend did not become ready at {base_url}")


def ensure_bom_openapi(base_url: str) -> None:
    with urllib.request.urlopen(f"{base_url.rstrip('/')}/openapi.json", timeout=20) as response:
        openapi = json.loads(response.read().decode("utf-8"))
    paths = openapi.get("paths", {})
    if "/api/bom" not in paths:
        raise RuntimeError("/api/bom is not exposed by the backend OpenAPI schema.")


def endpoint_ok(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def create_bom_load(
    client: BomLoadClient,
    state: LoadState,
    products: list[str],
    boms_per_product: int,
    lines_per_bom: int,
    concurrency: int,
) -> None:
    tasks = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        for product in products:
            for bom_no in range(1, boms_per_product + 1):
                tasks.append(
                    executor.submit(
                        create_one_bom_with_lines,
                        client,
                        state,
                        product,
                        bom_no,
                        lines_per_bom,
                    )
                )
        for task in as_completed(tasks):
            task.result()


def create_one_bom_with_lines(
    client: BomLoadClient,
    state: LoadState,
    product: str,
    bom_no: int,
    lines_per_bom: int,
) -> None:
    is_primary = 1 if bom_no == 1 else 0
    bom_code = f"{state.run_prefix}-{product}-BOM-{bom_no:02d}"
    _, created = client.request(
        "POST",
        "/api/bom",
        {
            "bom_code": bom_code,
            "bom_name": f"Load recipe {bom_no} for {product}",
            "target_articul": product,
            "bom_kind": "FINISHED_GOODS",
            "base_qty": 1000,
            "base_unit_code": "KG",
            "is_primary": is_primary,
            "valid_from": "2026-01-01",
            "valid_to": "2026-12-31",
            "created_by": "load-test",
        },
        metric_endpoint="POST /api/bom",
    )
    bom_id = int(created["id"])
    state.add_bom_id(bom_id)

    for line_no in range(1, lines_per_bom + 1):
        component_type = "PACKAGING" if line_no % 10 == 0 else "RAW"
        client.request(
            "POST",
            f"/api/bom/{bom_id}/lines",
            {
                "line_no": line_no * 10,
                "component_type": component_type,
                "component_articul": f"{product[:30]}R{line_no:09d}",
                "component_name": f"Load component {line_no}",
                "qty_per_base": round(5 + line_no * 1.5, 3),
                "unit_code": "KG" if component_type == "RAW" else "PCS",
                "loss_percent": 1.5 if component_type == "RAW" else 0,
                "created_by": "load-test",
            },
            metric_endpoint="POST /api/bom/{id}/lines",
        )

    if bom_no in {1, 2}:
        client.request(
            "POST",
            f"/api/bom/{bom_id}/approve",
            {"user_name": "load-test"},
            metric_endpoint="POST /api/bom/{id}/approve",
        )
        if is_primary:
            state.add_primary(product, bom_id)


def conflict_test(client: BomLoadClient, state: LoadState) -> None:
    product = (f"L{random_suffix(5)}CF" + ("Z" * 40))[:40]
    ids = []
    for idx in range(1, 3):
        _, created = client.request(
            "POST",
            "/api/bom",
            {
                "bom_code": f"{state.run_prefix}-{product}-BOM-{idx}",
                "bom_name": "Primary conflict test",
                "target_articul": product,
                "base_qty": 1000,
                "base_unit_code": "KG",
                "is_primary": 1,
                "valid_from": "2026-01-01",
                "valid_to": "2026-12-31",
                "created_by": "load-test",
            },
            metric_endpoint="POST /api/bom",
        )
        bom_id = int(created["id"])
        ids.append(bom_id)
        state.add_bom_id(bom_id)
        client.request(
            "POST",
            f"/api/bom/{bom_id}/lines",
            {
                "line_no": 10,
                "component_type": "RAW",
                "component_articul": f"{product[:30]}RAW0000000",
                "component_name": "Conflict raw",
                "qty_per_base": 100,
                "unit_code": "KG",
                "created_by": "load-test",
            },
            metric_endpoint="POST /api/bom/{id}/lines",
        )

    client.request(
        "POST",
        f"/api/bom/{ids[0]}/approve",
        {"user_name": "load-test"},
        metric_endpoint="POST /api/bom/{id}/approve",
    )
    client.request(
        "POST",
        f"/api/bom/{ids[1]}/approve",
        {"user_name": "load-test"},
        expected_statuses={400, 409, 422, 500},
        metric_endpoint="POST /api/bom/{id}/approve expected-conflict",
    )
    state.add_expected_conflict()


def concurrent_calculate(
    client: BomLoadClient,
    state: LoadState,
    calculate_requests: int,
    concurrency: int,
) -> None:
    approved_ids = list(state.approved_primary.values())
    if not approved_ids:
        raise RuntimeError("No approved primary BOMs were created.")
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        tasks = [
            executor.submit(calculate_once, client, random.choice(approved_ids), idx)
            for idx in range(calculate_requests)
        ]
        for task in as_completed(tasks):
            task.result()


def calculate_once(client: BomLoadClient, bom_id: int, idx: int) -> None:
    planned_qty = 500 + (idx % 50) * 100
    _, result = client.request(
        "POST",
        f"/api/bom/{bom_id}/calculate",
        {"planned_qty": planned_qty, "unit_code": "KG"},
        metric_endpoint="POST /api/bom/{id}/calculate",
    )
    lines = result.get("lines") or []
    if not lines or "required_qty" not in lines[0]:
        raise RuntimeError(f"Calculate response is malformed for BOM {bom_id}")


def default_lookup(client: BomLoadClient, state: LoadState, products: list[str], concurrency: int) -> None:
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        tasks = [
            executor.submit(default_lookup_once, client, product)
            for product in products
            for _ in range(3)
        ]
        for task in as_completed(tasks):
            task.result()


def default_lookup_once(client: BomLoadClient, product: str) -> None:
    query = urllib.parse.urlencode({"target_articul": product, "planned_date": "2026-05-17"})
    _, result = client.request(
        "GET",
        f"/api/bom/default?{query}",
        metric_endpoint="GET /api/bom/default",
    )
    if not result.get("bom_id"):
        raise RuntimeError(f"Default BOM was not found for {product}")


def list_and_detail_reads(client: BomLoadClient, state: LoadState, concurrency: int) -> None:
    ids = state.created_bom_ids[:]
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        tasks = []
        for _ in range(max(10, min(100, len(ids)))):
            tasks.append(executor.submit(client.request, "GET", "/api/bom?limit=100", None, {200}, "GET /api/bom"))
        for bom_id in ids:
            tasks.append(
                executor.submit(
                    client.request,
                    "GET",
                    f"/api/bom/{bom_id}",
                    None,
                    {200},
                    "GET /api/bom/{id}",
                )
            )
        for task in as_completed(tasks):
            task.result()


def cleanup_load_data() -> None:
    if oracledb is None:
        raise RuntimeError("oracledb is required for cleanup but is not installed.")
    user = os.getenv("WMS_ORACLE_USER", "RABAEV")
    password = os.getenv("WMS_ORACLE_PASSWORD", "RABAEVWMS")
    dsn = os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl")
    statements = [
        """
        delete from RRL_TRACE_EVENT
         where ENTITY_TYPE = 'BOM'
           and ENTITY_ID in (
             select to_char(BOM_ID)
               from RRL_BOM
              where BOM_CODE like 'LOAD-BOM-%'
           )
        """,
        """
        delete from RRL_BOM_AUDIT
         where BOM_ID in (
           select BOM_ID
             from RRL_BOM
            where BOM_CODE like 'LOAD-BOM-%'
         )
        """,
        """
        delete from RRL_BOM_LINE
         where BOM_ID in (
           select BOM_ID
             from RRL_BOM
            where BOM_CODE like 'LOAD-BOM-%'
         )
        """,
        "delete from RRL_BOM where BOM_CODE like 'LOAD-BOM-%'",
    ]
    with oracledb.connect(user=user, password=password, dsn=dsn) as connection:
        cursor = connection.cursor()
        for statement in statements:
            cursor.execute(statement)
        connection.commit()


def count_load_rows() -> dict[str, int]:
    if oracledb is None:
        return {}
    user = os.getenv("WMS_ORACLE_USER", "RABAEV")
    password = os.getenv("WMS_ORACLE_PASSWORD", "RABAEVWMS")
    dsn = os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl")
    sql = """
    select 'RRL_BOM' table_name, count(*) rows_found
      from RRL_BOM
     where BOM_CODE like 'LOAD-BOM-%'
    union all
    select 'RRL_BOM_LINE', count(*)
      from RRL_BOM_LINE
     where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE like 'LOAD-BOM-%')
    union all
    select 'RRL_BOM_AUDIT', count(*)
      from RRL_BOM_AUDIT
     where BOM_ID in (select BOM_ID from RRL_BOM where BOM_CODE like 'LOAD-BOM-%')
    """
    with oracledb.connect(user=user, password=password, dsn=dsn) as connection:
        cursor = connection.cursor()
        cursor.execute(sql)
        return {row[0]: int(row[1]) for row in cursor.fetchall()}


def build_report(state: LoadState, started_at: str, finished_at: str, args: argparse.Namespace) -> dict[str, Any]:
    metrics = state.metrics
    elapsed = (
        datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
        - datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    ).total_seconds()
    latencies = [m.elapsed_ms for m in metrics]
    by_endpoint: dict[str, list[RequestMetric]] = {}
    for metric in metrics:
        by_endpoint.setdefault(metric.endpoint, []).append(metric)

    return {
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_sec": round(elapsed, 3),
        "run_prefix": state.run_prefix,
        "parameters": {
            "base_url": args.base_url,
            "products": args.products,
            "boms_per_product": args.boms_per_product,
            "lines_per_bom": args.lines_per_bom,
            "concurrency": args.concurrency,
            "calculate_requests": args.calculate_requests,
        },
        "total_requests": len(metrics),
        "success_requests": sum(1 for m in metrics if m.ok),
        "failed_requests": sum(1 for m in metrics if not m.ok),
        "expected_conflicts": state.expected_conflicts,
        "requests_per_second": round(len(metrics) / elapsed, 3) if elapsed > 0 else 0,
        "latency_ms": latency_summary(latencies),
        "per_endpoint": {
            endpoint: endpoint_summary(items)
            for endpoint, items in sorted(by_endpoint.items())
        },
        "created": {
            "bom_count": len(state.created_bom_ids),
            "line_count": args.products * args.boms_per_product * args.lines_per_bom + 2,
        },
        "errors": [
            {
                "endpoint": metric.endpoint,
                "status_code": metric.status_code,
                "message": metric.error,
                "sample_body": metric.body,
            }
            for metric in metrics
            if not metric.ok
        ][:50],
    }


def endpoint_summary(items: list[RequestMetric]) -> dict[str, Any]:
    latencies = [item.elapsed_ms for item in items]
    return {
        "count": len(items),
        "success": sum(1 for item in items if item.ok),
        "failed": sum(1 for item in items if not item.ok),
        "p95": percentile(latencies, 95),
    }


def latency_summary(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
    return {
        "min": round(min(values), 3),
        "p50": round(median(values), 3),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": round(max(values), 3),
    }


def percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((pct / 100) * (len(ordered) - 1))))
    return round(ordered[index], 3)


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def report_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "duration_sec": report["duration_sec"],
        "total_requests": report["total_requests"],
        "success_requests": report["success_requests"],
        "failed_requests": report["failed_requests"],
        "requests_per_second": report["requests_per_second"],
        "latency_ms": report["latency_ms"],
        "created": report["created"],
    }


def normalize_endpoint(method: str, path: str) -> str:
    clean = path.split("?", 1)[0]
    parts = clean.strip("/").split("/")
    normalized = []
    for part in parts:
        normalized.append("{id}" if part.isdigit() else part)
    return f"{method} /{'/'.join(normalized)}"


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current.parent, *current.parents]:
        if (parent / ".git").exists():
            return parent
    return Path.cwd()


def random_suffix(length: int) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
