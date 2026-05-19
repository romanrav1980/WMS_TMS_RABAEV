from __future__ import annotations

import argparse
import base64
import json
import os
import random
import string
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
LOAD_PREFIX = "LOAD-WAVE"


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
    lock: Lock = field(default_factory=Lock)

    def add_metric(self, metric: RequestMetric) -> None:
        with self.lock:
            self.metrics.append(metric)


class ApiClient:
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

    def get(self, path: str, metric_endpoint: str | None = None) -> Any:
        return self.request("GET", path, metric_endpoint=metric_endpoint)[1]

    def post(self, path: str, payload: dict[str, Any], metric_endpoint: str | None = None) -> Any:
        return self.request("POST", path, payload=payload, metric_endpoint=metric_endpoint)[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave replenishment warehouse-task load test.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--waves", type=int, default=6)
    parser.add_argument("--orders-per-wave", type=int, default=2)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--execute-tasks", action="store_true")
    parser.add_argument("--replenishment-method", choices=["IMMEDIATE", "MINIMAX"], default="IMMEDIATE")
    parser.add_argument("--auto-minimax-trigger", action="store_true")
    parser.add_argument("--shelf-life-scenario", action="store_true")
    parser.add_argument("--dynamic-pick-faces", type=int, default=0)
    parser.add_argument("--drain-replenishment-queue", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--report", default="tests/load/wave/report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_prefix = f"{LOAD_PREFIX}-{random_suffix(6)}"
    if args.auto_minimax_trigger and (args.replenishment_method != "MINIMAX" or args.orders_per_wave < 3):
        raise ValueError("--auto-minimax-trigger requires --replenishment-method MINIMAX and --orders-per-wave >= 3.")
    if args.shelf_life_scenario and args.orders_per_wave < 3:
        raise ValueError("--shelf-life-scenario requires --orders-per-wave >= 3 to cover 70%, 50%, and FEFO customers.")
    state = LoadState(run_prefix=run_prefix)
    client = ApiClient(args.base_url, args.username, args.password, state)

    wait_for_api(client)
    cleanup_load_data()
    fixture = create_fixture(
        run_prefix,
        args.waves * args.orders_per_wave,
        args.replenishment_method,
        args.shelf_life_scenario,
        args.dynamic_pick_faces,
    )

    started = time.perf_counter()
    wave_inputs = []
    for wave_idx in range(args.waves):
        plan_ids = fixture["pick_plan_ids"][
            wave_idx * args.orders_per_wave : (wave_idx + 1) * args.orders_per_wave
        ]
        wave_inputs.append((wave_idx + 1, plan_ids, fixture["ware_id"]))

    with ThreadPoolExecutor(max_workers=max(args.concurrency, 1)) as executor:
        futures = [
            executor.submit(
                run_wave,
                client,
                run_prefix,
                idx,
                plan_ids,
                ware_id,
                args.execute_tasks,
                args.replenishment_method,
                args.auto_minimax_trigger,
                args.shelf_life_scenario,
                fixture["articul"],
                fixture["pick_cell"],
                fixture.get("expected_source_pallet"),
                args.dynamic_pick_faces,
                args.drain_replenishment_queue,
            )
            for idx, plan_ids, ware_id in wave_inputs
        ]
        for future in as_completed(futures):
            future.result()

    diagnostics = collect_diagnostics(run_prefix)
    assert_diagnostics(
        diagnostics,
        expected_waves=args.waves,
        dynamic_pick_faces=args.dynamic_pick_faces,
        drain_replenishment_queue=args.drain_replenishment_queue,
    )
    elapsed_s = time.perf_counter() - started
    report = build_report(state, diagnostics, elapsed_s, args)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.cleanup:
        cleanup_load_data()
        remaining = count_load_rows()
        print(json.dumps({"cleanup": "done", "remaining": remaining}, ensure_ascii=False))


def wait_for_api(client: ApiClient) -> None:
    for _ in range(30):
        try:
            client.get("/health", metric_endpoint="GET /health")
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("API did not become healthy.")


def run_wave(
    client: ApiClient,
    run_prefix: str,
    wave_idx: int,
    plan_ids: list[int],
    ware_id: int,
    execute_tasks: bool,
    replenishment_method: str,
    auto_minimax_trigger: bool,
    shelf_life_scenario: bool,
    articul: str,
    pick_cell: str,
    expected_source_pallet: str | None,
    dynamic_pick_faces: int,
    drain_replenishment_queue: bool,
) -> None:
    wave = client.post(
        "/api/picking/waves",
        {
            "wave_code": f"{run_prefix}-W{wave_idx:03d}",
            "wave_name": f"{run_prefix} wave {wave_idx:03d}",
            "ware_id": ware_id,
            "max_customers": 30,
            "created_by": run_prefix,
        },
        metric_endpoint="POST /api/picking/waves",
    )
    wave_id = int(wave["pick_wave_id"])
    for plan_id in plan_ids:
        client.post(
            f"/api/picking/waves/{wave_id}/plans",
            {"pick_plan_id": plan_id, "created_by": run_prefix},
            metric_endpoint="POST /api/picking/waves/{id}/plans",
        )
    client.post(
        f"/api/picking/waves/{wave_id}/calculate",
        {"updated_by": run_prefix},
        metric_endpoint="POST /api/picking/waves/{id}/calculate",
    )
    if auto_minimax_trigger:
        seed_pick_face_stock(run_prefix, wave_id, articul, pick_cell, len(plan_ids) - 1)
    client.post(
        f"/api/picking/waves/{wave_id}/launch",
        {"updated_by": run_prefix},
        metric_endpoint="POST /api/picking/waves/{id}/launch",
    )
    readiness_after_launch = client.get(
        f"/api/picking/waves/{wave_id}/readiness",
        metric_endpoint="GET /api/picking/waves/{id}/readiness",
    )
    if readiness_after_launch.get("is_ready"):
        raise AssertionError(f"Wave {wave_id} should not be ready immediately after launch.")
    replenishment = client.get(
        f"/api/picking/waves/{wave_id}/replenishment-tasks?limit=500",
        metric_endpoint="GET /api/picking/waves/{id}/replenishment-tasks",
    )
    if not replenishment:
        raise AssertionError(f"Wave {wave_id} did not create replenishment tasks.")
    active_replenishment = [row for row in replenishment if row.get("status") != "CANCELLED"]
    if replenishment_method == "MINIMAX":
        if not active_replenishment:
            raise AssertionError(f"Wave {wave_id} did not keep active Minimax replenishment rows.")
        waiting_statuses = {"WAIT_MINIMAX", "QUEUED", "WAIT_FREE_CELL"}
        if not all(row.get("status") in waiting_statuses and not row.get("warehouse_task_id") for row in active_replenishment):
            raise AssertionError(f"Wave {wave_id} minimax replenishment was not waiting before trigger.")
        if auto_minimax_trigger:
            wave_tasks = client.get(
                f"/api/picking/waves/{wave_id}/tasks?limit=500",
                metric_endpoint="GET /api/picking/waves/{id}/tasks",
            )
            case_pick_tasks = [row for row in wave_tasks if row.get("task_type") == "CASE_PICK"]
            if not case_pick_tasks:
                raise AssertionError(f"Wave {wave_id} has no CASE_PICK tasks for automatic Minimax trigger.")
            task = case_pick_tasks[0]
            result = client.post(
                f"/api/picking/waves/{wave_id}/tasks/{task['pick_task_id']}/complete",
                {
                    "completed_by": run_prefix,
                    "fact_qty": 1,
                    "scanned_pallet": task.get("pallet_uid"),
                    "scanned_from_cell": task.get("source_cell_code"),
                    "scanned_to_cell": task.get("target_cell_code"),
                    "adjust_pick_face_stock": True,
                },
                metric_endpoint="POST /api/picking/waves/{id}/tasks/{id}/complete",
            )
            if int(result.get("released_minimax_count") or 0) <= 0:
                raise AssertionError(f"Wave {wave_id} case-pick fact did not release Minimax replenishment.")
        else:
            client.post(
                f"/api/picking/waves/{wave_id}/replenishment/minimax-check",
                {"updated_by": run_prefix},
                metric_endpoint="POST /api/picking/waves/{id}/replenishment/minimax-check",
            )
        replenishment = client.get(
            f"/api/picking/waves/{wave_id}/replenishment-tasks?limit=500",
            metric_endpoint="GET /api/picking/waves/{id}/replenishment-tasks",
        )
    active_replenishment = [row for row in replenishment if row.get("status") != "CANCELLED"]
    driver_replenishment = [row for row in active_replenishment if row.get("warehouse_task_id")]
    missing_driver_task = [
        row
        for row in active_replenishment
        if row.get("status") in {"RELEASED", "ASSIGNED", "IN_PROGRESS", "DONE"}
        and not row.get("warehouse_task_id")
    ]
    if missing_driver_task:
        raise AssertionError(f"Wave {wave_id} released replenishment tasks are missing warehouse_task_id.")
    readiness_summary = readiness_after_launch.get("summary") or {}
    if int(readiness_summary.get("open_replenishment_count") or 0) != len(active_replenishment):
        raise AssertionError(f"Wave {wave_id} readiness does not report open replenishment tasks.")
    if active_replenishment and not driver_replenishment:
        raise AssertionError(f"Wave {wave_id} did not release any driver-facing replenishment task.")
    if dynamic_pick_faces > 0 and replenishment_method == "IMMEDIATE":
        expected_driver_tasks = min(len(active_replenishment), dynamic_pick_faces + 1)
        if len(driver_replenishment) < expected_driver_tasks:
            raise AssertionError(
                f"Wave {wave_id} released {len(driver_replenishment)} driver tasks, "
                f"expected at least {expected_driver_tasks} with dynamic pick faces."
            )
    if shelf_life_scenario:
        validate_shelf_life_replenishment(wave_id, driver_replenishment, expected_source_pallet)
    if execute_tasks or drain_replenishment_queue:
        max_rounds = len(active_replenishment) + 2 if drain_replenishment_queue else 1
        executed_task_ids: set[int] = set()
        for _ in range(max_rounds):
            replenishment_round = client.get(
                f"/api/picking/waves/{wave_id}/replenishment-tasks?limit=500",
                metric_endpoint="GET /api/picking/waves/{id}/replenishment-tasks",
            )
            open_driver_rows = [
                row
                for row in replenishment_round
                if row.get("warehouse_task_id")
                and row.get("warehouse_task_status") != "DONE"
                and int(row["warehouse_task_id"]) not in executed_task_ids
            ]
            if not open_driver_rows:
                if not drain_replenishment_queue:
                    break
                active_remaining = [row for row in replenishment_round if row.get("status") != "CANCELLED"]
                if all(row.get("status") == "DONE" for row in active_remaining):
                    break
                client.post(
                    f"/api/picking/waves/{wave_id}/replenishment/minimax-check",
                    {"updated_by": run_prefix},
                    metric_endpoint="POST /api/picking/waves/{id}/replenishment/minimax-check",
                )
                continue
            for row in open_driver_rows:
                execute_replenishment_task(client, run_prefix, row)
                executed_task_ids.add(int(row["warehouse_task_id"]))
                client.post(
                    f"/api/picking/waves/{wave_id}/replenishment/minimax-check",
                    {"updated_by": run_prefix},
                    metric_endpoint="POST /api/picking/waves/{id}/replenishment/minimax-check",
                )
        replenishment_after_execute = client.get(
            f"/api/picking/waves/{wave_id}/replenishment-tasks?limit=500",
            metric_endpoint="GET /api/picking/waves/{id}/replenishment-tasks",
        )
        active_after_execute = [row for row in replenishment_after_execute if row.get("status") != "CANCELLED"]
        executed_after = [row for row in active_after_execute if row.get("warehouse_task_id")]
        if not all(row.get("status") == "DONE" and row.get("warehouse_task_status") == "DONE" for row in executed_after):
            raise AssertionError(f"Wave {wave_id} replenishment tasks did not synchronize DONE status.")
        if drain_replenishment_queue and not all(row.get("status") == "DONE" for row in active_after_execute):
            raise AssertionError(f"Wave {wave_id} replenishment queue did not drain to DONE.")
        if drain_replenishment_queue:
            readiness_after_drain = client.get(
                f"/api/picking/waves/{wave_id}/readiness",
                metric_endpoint="GET /api/picking/waves/{id}/readiness",
            )
            drain_summary = readiness_after_drain.get("summary") or {}
            if int(drain_summary.get("open_replenishment_count") or 0) != 0:
                raise AssertionError(f"Wave {wave_id} readiness still reports replenishment blockers after drain.")
            if int(drain_summary.get("sync_error_count") or 0) != 0:
                raise AssertionError(f"Wave {wave_id} readiness reports domain sync blockers after drain.")
    client.get(
        f"/api/warehouse-tasks?task_type=REPLENISHMENT&limit=500",
        metric_endpoint="GET /api/warehouse-tasks?task_type=REPLENISHMENT",
    )


def execute_replenishment_task(client: ApiClient, run_prefix: str, row: dict[str, Any]) -> None:
    warehouse_task_id = int(row["warehouse_task_id"])
    qty = float(row.get("qty") or 0)
    client.post(
        f"/api/warehouse-tasks/{warehouse_task_id}/assign",
        {"assigned_to": f"{run_prefix}-DRIVER", "updated_by": run_prefix},
        metric_endpoint="POST /api/warehouse-tasks/{id}/assign",
    )
    client.post(
        f"/api/warehouse-tasks/{warehouse_task_id}/start",
        {"assigned_to": f"{run_prefix}-DRIVER", "updated_by": run_prefix},
        metric_endpoint="POST /api/warehouse-tasks/{id}/start",
    )
    client.post(
        f"/api/warehouse-tasks/{warehouse_task_id}/complete",
        {
            "assigned_to": f"{run_prefix}-DRIVER",
            "updated_by": run_prefix,
            "fact_qty": qty,
            "scanned_pallet": row.get("pallet_uid"),
            "scanned_from_cell": row.get("source_cell_code"),
            "scanned_to_cell": row.get("target_cell_code"),
        },
        metric_endpoint="POST /api/warehouse-tasks/{id}/complete",
    )


def create_fixture(
    run_prefix: str,
    order_count: int,
    replenishment_method: str,
    shelf_life_scenario: bool,
    dynamic_pick_faces: int,
) -> dict[str, Any]:
    with connect() as connection:
        cursor = connection.cursor()
        if shelf_life_scenario:
            fixture = create_shelf_life_stock_fixture(cursor, run_prefix)
            articul = fixture["articul"]
            ware_id = fixture["ware_id"]
            expected_source_pallet = fixture["expected_source_pallet"]
        else:
            fixture = create_generic_source_fixture(cursor, run_prefix, order_count)
            articul = fixture["articul"]
            ware_id = fixture["ware_id"]
            expected_source_pallet = None
        pick_cell = f"{run_prefix[-6:]}-PF"
        route_id = call_number(
            cursor,
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_route(
                p_route_code => :route_code,
                p_route_name => :route_name,
                p_ware_id => :ware_id,
                p_route_kind => 'PICK',
                p_active => 1,
                p_updated_by => :updated_by
              );
            end;
            """,
            {
                "route_code": f"{run_prefix}-ROUTE",
                "route_name": f"{run_prefix} route",
                "ware_id": ware_id,
                "updated_by": run_prefix,
            },
        )
        route_cell_id = call_number(
            cursor,
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_route_cell(
                p_pick_route_id => :route_id,
                p_cell_code => :cell_code,
                p_pick_sequence => 10,
                p_zone_code => :zone_code,
                p_active => 1,
                p_updated_by => :updated_by
              );
            end;
            """,
            {
                "route_id": route_id,
                "cell_code": pick_cell,
                "zone_code": "LOAD",
                "updated_by": run_prefix,
            },
        )
        pick_face_id = call_number(
            cursor,
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.upsert_pick_face(
                p_ware_id => :ware_id,
                p_cell_code => :cell_code,
                p_pick_face_code => :pick_face_code,
                p_pick_face_type => 'REGULAR',
                p_pick_route_id => :route_id,
                p_pick_route_cell_id => :route_cell_id,
                p_min_case_qty => 0,
                p_max_case_qty => 1000000,
                p_replenishment_trigger_qty => 1,
                p_active => 1,
                p_updated_by => :updated_by
              );
            end;
            """,
            {
                "ware_id": ware_id,
                "cell_code": pick_cell,
                "pick_face_code": f"{run_prefix}-PF",
                "route_id": route_id,
                "route_cell_id": route_cell_id,
                "updated_by": run_prefix,
            },
        )
        pick_face_articul_id = call_number(
            cursor,
            """
            begin
              :result := RRL_PICK_TOPOLOGY_API.assign_articul(
                p_pick_face_id => :pick_face_id,
                p_articul => :articul,
                p_priority => 1,
                p_case_pick_enabled => 1,
                p_active => 1,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"pick_face_id": pick_face_id, "articul": articul, "updated_by": run_prefix},
        )
        cursor.execute(
            """
            update RRL_PICK_FACE_ARTICUL
               set REPLENISHMENT_METHOD = :replenishment_method,
                   REPLENISHMENT_QTY_MODE = 'FILL_TO_VOLUME',
                   MIN_TRIGGER_BOX_QTY = 1,
                   BOXES_PER_LAYER = 10,
                   BOXES_PER_PALLET = 100,
                   BOX_VOLUME_M3 = 1,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = :updated_by
             where PICK_FACE_ARTICUL_ID = :pick_face_articul_id
            """,
            {
                "pick_face_articul_id": pick_face_articul_id,
                "replenishment_method": replenishment_method,
                "updated_by": run_prefix,
            },
        )
        for idx in range(1, dynamic_pick_faces + 1):
            dynamic_cell = f"{run_prefix[-6:]}-DYN{idx:02d}"
            ensure_load_cell(cursor, dynamic_cell, ware_id, x=200 + idx)
            call_number(
                cursor,
                """
                begin
                  :result := RRL_PICK_TOPOLOGY_API.upsert_pick_face(
                    p_ware_id => :ware_id,
                    p_cell_code => :cell_code,
                    p_pick_face_code => :pick_face_code,
                    p_pick_face_type => 'DYNAMIC',
                    p_min_case_qty => 0,
                    p_max_case_qty => 1000000,
                    p_replenishment_trigger_qty => 0,
                    p_active => 1,
                    p_updated_by => :updated_by
                  );
                end;
                """,
                {
                    "ware_id": ware_id,
                    "cell_code": dynamic_cell,
                    "pick_face_code": f"{run_prefix}-DYN{idx:02d}",
                    "updated_by": run_prefix,
                },
            )

        pick_plan_ids: list[int] = []
        for order_idx in range(1, order_count + 1):
            customer_id = next_sequence(cursor, "RRL_CUSTOMER_SQ")
            order_id = next_sequence(cursor, "RRL_CUSTOMER_ORDER_SQ")
            row_id = next_sequence(cursor, "RRL_CUSTOMER_ORDER_ROW_SQ")
            cursor.execute(
                """
                insert into RRL_CUSTOMER (
                  CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE, ACTIVE, CREATED_AT, CREATED_BY
                ) values (
                  :customer_id, :customer_code, :customer_name, 'STORE', 1, sysdate, :created_by
                )
                """,
                {
                    "customer_id": customer_id,
                    "customer_code": f"{run_prefix}-C{order_idx:04d}",
                    "customer_name": f"{run_prefix} customer {order_idx:04d}",
                    "created_by": run_prefix,
                },
            )
            if shelf_life_scenario:
                shelf_life_percent = 70 if order_idx % 3 == 1 else 50 if order_idx % 3 == 2 else None
                if shelf_life_percent is not None:
                    cursor.execute(
                        """
                        insert into RRL_CUSTOMER_PRODUCT_RULE (
                          CUSTOMER_PRODUCT_RULE_ID, CUSTOMER_ID, ARTICUL,
                          MIN_SHELF_LIFE_PERCENT, RULE_PRIORITY, ACTIVE,
                          VALID_FROM, CREATED_AT, CREATED_BY
                        ) values (
                          RRL_CUSTOMER_PRODUCT_RULE_SQ.nextval, :customer_id, :articul,
                          :shelf_life_percent, 10, 1,
                          trunc(sysdate), sysdate, :created_by
                        )
                        """,
                        {
                            "customer_id": customer_id,
                            "articul": articul,
                            "shelf_life_percent": shelf_life_percent,
                            "created_by": run_prefix,
                        },
                    )
            cursor.execute(
                """
                insert into RRL_CUSTOMER_ORDER (
                  CUSTOMER_ORDER_ID, ORDER_NO, CUSTOMER_ID, WARE_ID, ORDER_DATE, SHIPMENT_DATE,
                  STATUS, SOURCE_SYSTEM, CREATED_AT, CREATED_BY
                ) values (
                  :order_id, :order_no, :customer_id, :ware_id, sysdate, trunc(sysdate),
                  'OPEN', 'LOAD', sysdate, :created_by
                )
                """,
                {
                    "order_id": order_id,
                    "order_no": f"{run_prefix}-O{order_idx:04d}",
                    "customer_id": customer_id,
                    "ware_id": ware_id,
                    "created_by": run_prefix,
                },
            )
            cursor.execute(
                """
                insert into RRL_CUSTOMER_ORDER_ROW (
                  CUSTOMER_ORDER_ROW_ID, CUSTOMER_ORDER_ID, LINE_NO, ARTICUL,
                  PRODUCT_NAME, UNIT_CODE, ORDER_QTY, STATUS, CREATED_AT, CREATED_BY
                ) values (
                  :row_id, :order_id, 10, :articul,
                  :product_name, 'PCS', 1, 'OPEN', sysdate, :created_by
                )
                """,
                {
                    "row_id": row_id,
                    "order_id": order_id,
                    "articul": articul,
                    "product_name": f"{run_prefix} product",
                    "created_by": run_prefix,
                },
            )
            pick_plan_id = call_number(
                cursor,
                """
                begin
                  :result := RRL_PICKING_API.create_plan(
                    p_customer_order_id => :order_id,
                    p_plan_strategy => 'FEFO',
                    p_created_by => :created_by
                  );
                end;
                """,
                {"order_id": order_id, "created_by": run_prefix},
            )
            pick_plan_ids.append(pick_plan_id)
        connection.commit()
        return {
            "articul": articul,
            "ware_id": ware_id,
            "pick_cell": pick_cell,
            "pick_plan_ids": pick_plan_ids,
            "expected_source_pallet": expected_source_pallet,
        }


def create_generic_source_fixture(cursor: oracledb.Cursor, run_prefix: str, source_count: int) -> dict[str, Any]:
    suffix = run_prefix[-6:]
    ware_id = 9103
    articul = f"{run_prefix}-SKU"
    cursor.execute(
        """
        merge into RRL_ARTICULS d
        using (
          select :articul ACTICUL,
                 :default_cell CELL
            from dual
        ) s
        on (d.ACTICUL = s.ACTICUL)
        when matched then update set
          d.NAME = :name,
          d.UNIT_TYPE = 'PCS',
          d.CELL = s.CELL,
          d.BESTBEFOREDAYS = 365,
          d.BARCODE_SHT = nvl(d.BARCODE_SHT, '777')
        when not matched then insert (
          ACTICUL, NORMA_UKLADKI, CELL, NAME, UNIT_TYPE, BARCODE_SHT,
          WEIGHT_OF_KOR, COUNT_IN_ROW, ROWS_IN_PAL, COUNT_SHT_IN_KOR,
          PALLET_MULTIPLE, CARTON_WEIGHT, ETAJ_LIMIT, BESTBEFOREDAYS,
          ABC_GROUP, XYZ_GROUP
        ) values (
          s.ACTICUL, 1, s.CELL, :name, 'PCS', '777',
          1, 10, 5, 1, 1, 0, 100, 365, 'B', 'Y'
        )
        """,
        {
            "articul": articul,
            "default_cell": f"{suffix}-S001",
            "name": f"{run_prefix} isolated product",
        },
    )
    for idx in range(1, source_count + 1):
        source_cell = f"{suffix}-S{idx:03d}"
        ensure_load_cell(cursor, source_cell, ware_id, x=300 + idx)
        seed_source_pallet(
            cursor,
            f"{run_prefix}-SRC-{idx:04d}",
            articul,
            source_cell,
            qty=10,
            produced_days_ago=idx,
            shelf_life_days=365,
        )
    return {"articul": articul, "ware_id": ware_id}


def create_shelf_life_stock_fixture(cursor: oracledb.Cursor, run_prefix: str) -> dict[str, Any]:
    suffix = run_prefix[-6:]
    ware_id = 9104
    articul = f"{run_prefix}-FRESH"
    source_cell_1 = f"{suffix}-S1"
    source_cell_2 = f"{suffix}-S2"
    expected_source_pallet = f"{run_prefix}-SRC-FRESH"
    ensure_load_cell(cursor, source_cell_1, ware_id, x=101)
    ensure_load_cell(cursor, source_cell_2, ware_id, x=102)
    cursor.execute(
        """
        merge into RRL_ARTICULS d
        using (
          select :articul ACTICUL,
                 :source_cell CELL
            from dual
        ) s
        on (d.ACTICUL = s.ACTICUL)
        when matched then update set
          d.NAME = :name,
          d.UNIT_TYPE = 'PCS',
          d.CELL = s.CELL,
          d.BESTBEFOREDAYS = 100,
          d.BARCODE_SHT = nvl(d.BARCODE_SHT, '777')
        when not matched then insert (
          ACTICUL, NORMA_UKLADKI, CELL, NAME, UNIT_TYPE, BARCODE_SHT,
          WEIGHT_OF_KOR, COUNT_IN_ROW, ROWS_IN_PAL, COUNT_SHT_IN_KOR,
          PALLET_MULTIPLE, CARTON_WEIGHT, ETAJ_LIMIT, BESTBEFOREDAYS,
          ABC_GROUP, XYZ_GROUP
        ) values (
          s.ACTICUL, 1, s.CELL, :name, 'PCS', '777',
          1, 10, 5, 1, 1, 0, 100, 100, 'B', 'Y'
        )
        """,
        {"articul": articul, "source_cell": source_cell_1, "name": f"{run_prefix} freshness product"},
    )
    seed_source_pallet(cursor, f"{run_prefix}-SRC-STALE", articul, source_cell_1, qty=100, produced_days_ago=90, shelf_life_days=100)
    seed_source_pallet(cursor, f"{run_prefix}-SRC-MID", articul, source_cell_1, qty=100, produced_days_ago=40, shelf_life_days=100)
    seed_source_pallet(cursor, expected_source_pallet, articul, source_cell_2, qty=100, produced_days_ago=20, shelf_life_days=100)
    return {"articul": articul, "ware_id": ware_id, "expected_source_pallet": expected_source_pallet}


def ensure_load_cell(cursor: oracledb.Cursor, cell: str, ware_id: int, x: int) -> None:
    cursor.execute(
        """
        merge into RRL_CELLS d
        using (
          select :cell CELL,
                 :ware_id WARE_ID
            from dual
        ) s
        on (d.CELL = s.CELL)
        when matched then update set
          d.WARE_ID = s.WARE_ID,
          d.X = :x,
          d.Y = 1,
          d.Z = 1,
          d.OTBOR = 0,
          d.BLOCKED_FOR_REMAINS = 0,
          d.BLOCKED_FOR_POPOLNENIE = 0,
          d.BLOCKED_FOR_ACCEPT = 0,
          d.LAST_TIME_OF_UPDATE = sysdate
        when not matched then insert (
          CELL, WARE_ID, X, Y, Z, OTBOR, BLOCKED_FOR_REMAINS,
          BLOCKED_FOR_POPOLNENIE, BLOCKED_FOR_ACCEPT, IS_SYSTEM,
          LAST_TIME_OF_UPDATE, LIMIT_WEIGHT, LIMIT_HEIGHT
        ) values (
          s.CELL, s.WARE_ID, :x, 1, 1, 0, 0,
          0, 0, 0, sysdate, 100000, 2500
        )
        """,
        {"cell": cell, "ware_id": ware_id, "x": x},
    )


def seed_source_pallet(
    cursor: oracledb.Cursor,
    uid_pallet: str,
    articul: str,
    cell: str,
    qty: int,
    produced_days_ago: int,
    shelf_life_days: int,
) -> None:
    cursor.execute(
        """
        merge into RRL_PALLETS d
        using (
          select :uid_pallet UID_PALLET,
                 :articul ARTICUL,
                 :qty UNIT_COUNT,
                 trunc(sysdate) - :produced_days_ago PRODUCED_DATE,
                 trunc(sysdate) - :produced_days_ago + :shelf_life_days EXPIRY_DATE
            from dual
        ) s
        on (d.UID_PALLET = s.UID_PALLET)
        when matched then update set
          d.ARTICUL = s.ARTICUL,
          d.UNIT_COUNT = s.UNIT_COUNT,
          d.PRODUCED_DATE = s.PRODUCED_DATE,
          d.EXPIRY_DATE = s.EXPIRY_DATE,
          d.QUALITY_STATUS = 'RELEASED'
        when not matched then insert (
          UID_PALLET, ARTICUL, CREATION_DATE, PRODUCED_DATE, EXPIRY_DATE,
          UNIT_COUNT, PRIHOD_NAKLAD_ID, PRINTED, KLADOVSHIK, QUALITY_STATUS
        ) values (
          s.UID_PALLET, s.ARTICUL, sysdate, s.PRODUCED_DATE, s.EXPIRY_DATE,
          s.UNIT_COUNT, 0, 0, substr(:created_by, 1, 15), 'RELEASED'
        )
        """,
        {
            "uid_pallet": uid_pallet,
            "articul": articul,
            "qty": qty,
            "produced_days_ago": produced_days_ago,
            "shelf_life_days": shelf_life_days,
            "created_by": uid_pallet,
        },
    )
    cursor.execute(
        """
        merge into RRL_REMAINS d
        using (
          select :uid_pallet UID_POLETA,
                 :cell CELL,
                 :qty REMAIN
            from dual
        ) s
        on (d.UID_POLETA = s.UID_POLETA and d.CELL = s.CELL)
        when matched then update set
          d.REMAIN = s.REMAIN
        when not matched then insert (
          UID_POLETA, CELL, REMAIN
        ) values (
          s.UID_POLETA, s.CELL, s.REMAIN
        )
        """,
        {"uid_pallet": uid_pallet, "cell": cell, "qty": qty},
    )


def validate_shelf_life_replenishment(
    wave_id: int,
    active_replenishment: list[dict[str, Any]],
    expected_source_pallet: str | None,
) -> None:
    if not expected_source_pallet:
        raise AssertionError("Shelf-life scenario has no expected source pallet.")
    if not active_replenishment:
        raise AssertionError(f"Wave {wave_id} has no active replenishment rows for shelf-life validation.")
    for row in active_replenishment:
        if row.get("pallet_uid") != expected_source_pallet:
            raise AssertionError(
                f"Wave {wave_id} selected {row.get('pallet_uid')} instead of freshness-compliant {expected_source_pallet}."
            )
        if float(row.get("min_shelf_life_percent") or 0) < 70:
            raise AssertionError(f"Wave {wave_id} did not store the strictest 70% shelf-life requirement.")


def seed_pick_face_stock(run_prefix: str, wave_id: int, articul: str, pick_cell: str, qty: int) -> None:
    if qty <= 0:
        return
    uid_pallet = f"{run_prefix}-PF-STOCK-{wave_id}"
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            merge into RRL_PALLETS d
            using (
              select :uid_pallet UID_PALLET,
                     :articul ARTICUL,
                     :qty UNIT_COUNT
                from dual
            ) s
            on (d.UID_PALLET = s.UID_PALLET)
            when matched then update set
              d.ARTICUL = s.ARTICUL,
              d.UNIT_COUNT = s.UNIT_COUNT,
              d.PRODUCED_DATE = trunc(sysdate),
              d.EXPIRY_DATE = trunc(sysdate) + 365,
              d.QUALITY_STATUS = 'RELEASED'
            when not matched then insert (
              UID_PALLET, ARTICUL, CREATION_DATE, PRODUCED_DATE, EXPIRY_DATE,
              UNIT_COUNT, PRIHOD_NAKLAD_ID, PRINTED, KLADOVSHIK, QUALITY_STATUS
            ) values (
              s.UID_PALLET, s.ARTICUL, sysdate, trunc(sysdate), trunc(sysdate) + 365,
              s.UNIT_COUNT, 0, 0, substr(:run_prefix, 1, 15), 'RELEASED'
            )
            """,
            {"uid_pallet": uid_pallet, "articul": articul, "qty": qty, "run_prefix": run_prefix},
        )
        cursor.execute(
            """
            merge into RRL_REMAINS d
            using (
              select :uid_pallet UID_POLETA,
                     :pick_cell CELL,
                     :qty REMAIN
                from dual
            ) s
            on (d.UID_POLETA = s.UID_POLETA and d.CELL = s.CELL)
            when matched then update set
              d.REMAIN = s.REMAIN
            when not matched then insert (
              UID_POLETA, CELL, REMAIN
            ) values (
              s.UID_POLETA, s.CELL, s.REMAIN
            )
            """,
            {"uid_pallet": uid_pallet, "pick_cell": pick_cell, "qty": qty},
        )
        connection.commit()


def select_stock_candidate(cursor: oracledb.Cursor) -> tuple[str, int, str]:
    cursor.execute(
        """
        select ARTICUL, WARE_ID, PICK_CELL
          from (
            select upper(substr(p.ARTICUL, 1, 40)) ARTICUL,
                   c.WARE_ID,
                   max(r.REMAIN) MAX_REMAIN,
                   min(c.CELL) PICK_CELL
              from RRL_REMAINS r
              join RRL_PALLETS p
                on p.UID_PALLET = r.UID_POLETA
              join RRL_CELLS c
                on c.CELL = r.CELL
             where r.REMAIN > 10
               and p.ARTICUL is not null
               and c.WARE_ID is not null
             group by p.ARTICUL, c.WARE_ID
             order by max(r.REMAIN) desc
          )
         where rownum = 1
        """
    )
    row = cursor.fetchone()
    if not row:
        raise RuntimeError("No stock candidate with remain > 10 was found.")
    return str(row[0]), int(row[1]), str(row[2])


def collect_diagnostics(run_prefix: str) -> dict[str, int]:
    with connect() as connection:
        cursor = connection.cursor()
        return {
            "waves": count(cursor, "RRL_PICK_WAVE", "CREATED_BY = :marker", marker=run_prefix),
            "launched_waves": count(
                cursor,
                "RRL_PICK_WAVE",
                "CREATED_BY = :marker and STATUS = 'LAUNCHED'",
                marker=run_prefix,
            ),
            "pick_plans": count(cursor, "RRL_PICK_PLAN", "CREATED_BY = :marker", marker=run_prefix),
            "wave_replenishment_tasks": count(
                cursor,
                "RRL_PICK_WAVE_REPLENISH_TASK",
                "CREATED_BY = :marker and STATUS <> 'CANCELLED'",
                marker=run_prefix,
            ),
            "queued_wave_replenishment_tasks": count(
                cursor,
                "RRL_PICK_WAVE_REPLENISH_TASK",
                "CREATED_BY = :marker and STATUS in ('QUEUED', 'WAIT_FREE_CELL', 'WAIT_MINIMAX')",
                marker=run_prefix,
            ),
            "source_reservations": count(
                cursor,
                "RRL_STOCK_RESERVATION",
                """
                CREATED_BY = :marker
                and RESERVATION_DOMAIN = 'WAVE'
                and SOURCE_DOC_TYPE = 'PICK_WAVE'
                and RESERVATION_KIND = 'HARD'
                and STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING', 'CONSUMED')
                """,
                marker=run_prefix,
            ),
            "active_source_reservations": count(
                cursor,
                "RRL_STOCK_RESERVATION",
                """
                CREATED_BY = :marker
                and RESERVATION_DOMAIN = 'WAVE'
                and SOURCE_DOC_TYPE = 'PICK_WAVE'
                and RESERVATION_KIND = 'HARD'
                and STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
                """,
                marker=run_prefix,
            ),
            "consumed_source_reservations": count(
                cursor,
                "RRL_STOCK_RESERVATION",
                """
                CREATED_BY = :marker
                and RESERVATION_DOMAIN = 'WAVE'
                and SOURCE_DOC_TYPE = 'PICK_WAVE'
                and RESERVATION_KIND = 'HARD'
                and STATUS = 'CONSUMED'
                """,
                marker=run_prefix,
            ),
            "warehouse_replenishment_tasks": count(
                cursor,
                "RRL_WAREHOUSE_TASK",
                """
                TASK_SOURCE = 'WAVE'
                and TASK_TYPE = 'REPLENISHMENT'
                and SOURCE_DOC_ID in (
                  select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
                )
                """,
                marker=run_prefix,
            ),
            "dynamic_warehouse_replenishment_tasks": count(
                cursor,
                "RRL_WAREHOUSE_TASK",
                """
                TASK_SOURCE = 'WAVE'
                and TASK_TYPE = 'REPLENISHMENT'
                and SOURCE_DOC_ID in (
                  select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
                )
                and TO_CELL like :dynamic_cell_like
                """,
                marker=run_prefix,
                dynamic_cell_like=f"{run_prefix[-6:]}-DYN%",
            ),
            "dynamic_pick_face_assignments": count(
                cursor,
                "RRL_PICK_FACE_ASSIGNMENT",
                """
                PICK_WAVE_ID in (
                  select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
                )
                and STATUS = 'ACTIVE'
                """,
                marker=run_prefix,
            ),
            "done_warehouse_replenishment_tasks": count(
                cursor,
                "RRL_WAREHOUSE_TASK",
                """
                TASK_SOURCE = 'WAVE'
                and TASK_TYPE = 'REPLENISHMENT'
                and STATUS = 'DONE'
                and SOURCE_DOC_ID in (
                  select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
                )
                """,
                marker=run_prefix,
            ),
            "done_wave_replenishment_tasks": count(
                cursor,
                "RRL_PICK_WAVE_REPLENISH_TASK",
                "CREATED_BY = :marker and STATUS = 'DONE'",
                marker=run_prefix,
            ),
            "warehouse_replenishment_sync_rows": count(
                cursor,
                "RRL_WAREHOUSE_TASK_SYNC",
                """
                TASK_SOURCE = 'WAVE'
                and TASK_TYPE = 'REPLENISHMENT'
                and TASK_ID in (
                  select TASK_ID
                    from RRL_WAREHOUSE_TASK
                   where TASK_SOURCE = 'WAVE'
                     and TASK_TYPE = 'REPLENISHMENT'
                     and SOURCE_DOC_ID in (
                       select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
                     )
                )
                """,
                marker=run_prefix,
            ),
            "synced_warehouse_replenishment_sync_rows": count(
                cursor,
                "RRL_WAREHOUSE_TASK_SYNC",
                """
                TASK_SOURCE = 'WAVE'
                and TASK_TYPE = 'REPLENISHMENT'
                and SYNC_STATUS = 'SYNCED'
                and TASK_ID in (
                  select TASK_ID
                    from RRL_WAREHOUSE_TASK
                   where TASK_SOURCE = 'WAVE'
                     and TASK_TYPE = 'REPLENISHMENT'
                     and SOURCE_DOC_ID in (
                       select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
                     )
                )
                """,
                marker=run_prefix,
            ),
            "warehouse_replenishment_duplicates": duplicate_warehouse_tasks(cursor, run_prefix),
            "source_reservation_duplicates": duplicate_source_reservations(cursor, run_prefix),
            "cancelled_replenishment_with_source_reservation": count(
                cursor,
                "RRL_PICK_WAVE_REPLENISH_TASK",
                """
                CREATED_BY = :marker
                and STATUS = 'CANCELLED'
                and SOURCE_RESERVATION_ID is not null
                """,
                marker=run_prefix,
            ),
            "invalid_objects": count(cursor, "USER_OBJECTS", "STATUS <> 'VALID'"),
        }


def assert_diagnostics(
    diagnostics: dict[str, int],
    expected_waves: int,
    dynamic_pick_faces: int = 0,
    drain_replenishment_queue: bool = False,
) -> None:
    if diagnostics["waves"] != expected_waves:
        raise AssertionError(f"Expected {expected_waves} waves, got {diagnostics['waves']}.")
    if diagnostics["launched_waves"] != expected_waves:
        raise AssertionError(f"Expected {expected_waves} launched waves, got {diagnostics['launched_waves']}.")
    if diagnostics["wave_replenishment_tasks"] <= 0:
        raise AssertionError("Expected wave replenishment tasks.")
    if diagnostics["source_reservations"] != diagnostics["wave_replenishment_tasks"]:
        raise AssertionError(
            "Source reservation count does not match wave replenishment task count: "
            f"{diagnostics['source_reservations']} vs {diagnostics['wave_replenishment_tasks']}."
        )
    if diagnostics["warehouse_replenishment_tasks"] <= 0:
        raise AssertionError("Expected at least one driver-facing warehouse replenishment task.")
    if diagnostics["warehouse_replenishment_tasks"] > diagnostics["wave_replenishment_tasks"]:
        raise AssertionError(
            "Warehouse replenishment task count exceeds wave replenishment task count: "
            f"{diagnostics['warehouse_replenishment_tasks']} vs {diagnostics['wave_replenishment_tasks']}."
        )
    if dynamic_pick_faces > 0:
        expected_dynamic_tasks = min(dynamic_pick_faces, max(diagnostics["wave_replenishment_tasks"] - 1, 0))
        if diagnostics["dynamic_warehouse_replenishment_tasks"] < expected_dynamic_tasks:
            raise AssertionError(
                "Dynamic pick-face warehouse replenishment task count is lower than expected: "
                f"{diagnostics['dynamic_warehouse_replenishment_tasks']} vs {expected_dynamic_tasks}."
            )
        if diagnostics["dynamic_pick_face_assignments"] < expected_dynamic_tasks:
            raise AssertionError(
                "Dynamic pick-face assignment count is lower than expected: "
                f"{diagnostics['dynamic_pick_face_assignments']} vs {expected_dynamic_tasks}."
            )
    if diagnostics["warehouse_replenishment_duplicates"] != 0:
        raise AssertionError("Duplicate warehouse replenishment tasks detected.")
    if diagnostics["source_reservation_duplicates"] != 0:
        raise AssertionError("Duplicate source pallet reservations detected.")
    if diagnostics["cancelled_replenishment_with_source_reservation"] != 0:
        raise AssertionError(
            "Cancelled replenishment rows must not keep source reservations: "
            f"{diagnostics['cancelled_replenishment_with_source_reservation']}."
        )
    if diagnostics["done_warehouse_replenishment_tasks"] > 0:
        if diagnostics["warehouse_replenishment_sync_rows"] != diagnostics["done_warehouse_replenishment_tasks"]:
            raise AssertionError(
                "Warehouse replenishment domain sync count does not match done task count: "
                f"{diagnostics['warehouse_replenishment_sync_rows']} vs {diagnostics['done_warehouse_replenishment_tasks']}."
            )
        if diagnostics["synced_warehouse_replenishment_sync_rows"] != diagnostics["done_warehouse_replenishment_tasks"]:
            raise AssertionError("Warehouse replenishment domain sync did not reach SYNCED.")
    if diagnostics["invalid_objects"] != 0:
        raise AssertionError(f"Oracle invalid objects detected: {diagnostics['invalid_objects']}.")
    if drain_replenishment_queue:
        if diagnostics["done_wave_replenishment_tasks"] != diagnostics["wave_replenishment_tasks"]:
            raise AssertionError(
                "Drained wave replenishment task count does not match domain task count: "
                f"{diagnostics['done_wave_replenishment_tasks']} vs {diagnostics['wave_replenishment_tasks']}."
            )
        if diagnostics["done_warehouse_replenishment_tasks"] != diagnostics["wave_replenishment_tasks"]:
            raise AssertionError(
                "Drained warehouse replenishment task count does not match domain task count: "
                f"{diagnostics['done_warehouse_replenishment_tasks']} vs {diagnostics['wave_replenishment_tasks']}."
            )
        if diagnostics["active_source_reservations"] != 0:
            raise AssertionError(f"Active source reservations remain after drain: {diagnostics['active_source_reservations']}.")
        if diagnostics["consumed_source_reservations"] != diagnostics["source_reservations"]:
            raise AssertionError(
                "Consumed source reservation count does not match source reservation count: "
                f"{diagnostics['consumed_source_reservations']} vs {diagnostics['source_reservations']}."
            )


def cleanup_load_data() -> None:
    with connect() as connection:
        cursor = connection.cursor()
        marker_like = f"{LOAD_PREFIX}-%"
        cursor.execute(
            """
            delete from RRL_CASE_PICK_EVENT
             where CREATED_BY like :marker_like
                or CASE_PICK_TASK_ID in (
                  select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CREATED_BY like :marker_like
                  union all
                  select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK
                   where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like)
                )
                or CASE_PICK_LINE_ID in (
                  select CASE_PICK_LINE_ID from RRL_CASE_PICK_LINE where CREATED_BY like :marker_like
                  union all
                  select CASE_PICK_LINE_ID from RRL_CASE_PICK_LINE
                   where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like)
                )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_INVENTORY_TASK
             where CREATED_BY like :marker_like
                or SOURCE_DOC_ID in (
                  select CASE_PICK_SHORT_ID
                    from RRL_CASE_PICK_SHORT
                   where CASE_PICK_TASK_ID in (
                     select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CREATED_BY like :marker_like
                     union all
                     select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK
                      where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like)
                   )
                )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_CASE_PICK_SHORT
             where CREATED_BY like :marker_like
                or CASE_PICK_TASK_ID in (
                  select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CREATED_BY like :marker_like
                  union all
                  select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK
                   where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like)
                )
                or CASE_PICK_LINE_ID in (
                  select CASE_PICK_LINE_ID from RRL_CASE_PICK_LINE where CREATED_BY like :marker_like
                  union all
                  select CASE_PICK_LINE_ID from RRL_CASE_PICK_LINE
                   where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like)
                )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_CASE_PICK_LINE
             where CREATED_BY like :marker_like
                or CASE_PICK_TASK_ID in (
                  select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CREATED_BY like :marker_like
                  union all
                  select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK
                   where PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like)
                )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_CASE_PICK_TASK
             where CREATED_BY like :marker_like
                or PICK_WAVE_ID in (select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like)
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_WAREHOUSE_TASK_SYNC
             where TASK_SOURCE = 'WAVE'
               and TASK_TYPE in ('REPLENISHMENT', 'PICKING_MOVE')
               and TASK_ID in (
                 select TASK_ID
                   from RRL_WAREHOUSE_TASK
                  where CREATED_BY like :marker_like
                    and TASK_SOURCE = 'WAVE'
                    and TASK_TYPE in ('REPLENISHMENT', 'PICKING_MOVE')
               )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_WAREHOUSE_TASK_STOCK_MOVE
             where TASK_ID in (
               select TASK_ID
                 from RRL_WAREHOUSE_TASK
                where CREATED_BY like :marker_like
                  and TASK_SOURCE = 'WAVE'
                  and TASK_TYPE in ('REPLENISHMENT', 'PICKING_MOVE')
             )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_PICK_FACE_ASSIGNMENT
             where PICK_WAVE_ID in (
               select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like
             )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_WAREHOUSE_TASK
             where CREATED_BY like :marker_like
               and TASK_SOURCE = 'WAVE'
               and TASK_TYPE in ('REPLENISHMENT', 'PICKING_MOVE')
            """,
            {"marker_like": marker_like},
        )
        cursor.execute(
            """
            delete from RRL_STOCK_RESERVATION
             where CREATED_BY like :marker_like
               and RESERVATION_DOMAIN = 'WAVE'
               and SOURCE_DOC_TYPE = 'PICK_WAVE'
            """,
            {"marker_like": marker_like},
        )
        cursor.execute("delete from RRL_REMAINS where UID_POLETA like :marker_like", {"marker_like": marker_like})
        cursor.execute("delete from RRL_PALLETS where UID_PALLET like :marker_like", {"marker_like": marker_like})
        for table in (
            "RRL_PICK_WAVE_AUDIT",
            "RRL_PICK_WAVE_TASK",
            "RRL_PICK_WAVE_REPLENISH_TASK",
            "RRL_PICK_WAVE_RESERVATION",
            "RRL_PICK_WAVE_SHORTAGE",
            "RRL_PICK_WAVE_DEMAND",
            "RRL_PICK_WAVE_LINE",
            "RRL_PICK_WAVE_ORDER",
        ):
            cursor.execute(
                f"""
                delete from {table}
                 where PICK_WAVE_ID in (
                   select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like
                 )
                """,
                {"marker_like": marker_like},
            )
        cursor.execute("delete from RRL_PICK_WAVE where CREATED_BY like :marker_like", {"marker_like": marker_like})
        for table in ("RRL_PICK_DECISION_LOG", "RRL_PICK_SHORTAGE", "RRL_PICK_RESERVATION", "RRL_PICK_TASK", "RRL_PICK_PLAN_LINE"):
            cursor.execute(
                f"""
                delete from {table}
                 where PICK_PLAN_ID in (
                   select PICK_PLAN_ID from RRL_PICK_PLAN where CREATED_BY like :marker_like
                 )
                """,
                {"marker_like": marker_like},
            )
        cursor.execute("delete from RRL_PICK_PLAN where CREATED_BY like :marker_like", {"marker_like": marker_like})
        cursor.execute(
            """
            delete from RRL_CUSTOMER_ORDER_ROW
             where CUSTOMER_ORDER_ID in (
               select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER where CREATED_BY like :marker_like
             )
            """,
            {"marker_like": marker_like},
        )
        cursor.execute("delete from RRL_CUSTOMER_ORDER where CREATED_BY like :marker_like", {"marker_like": marker_like})
        cursor.execute("delete from RRL_CUSTOMER_PRODUCT_RULE where CREATED_BY like :marker_like", {"marker_like": marker_like})
        cursor.execute("delete from RRL_CUSTOMER where CREATED_BY like :marker_like", {"marker_like": marker_like})
        cursor.execute(
            """
            delete from RRL_PICK_FACE_ARTICUL
             where CREATED_BY like :marker_like
               and PICK_FACE_ID in (select PICK_FACE_ID from RRL_PICK_FACE where CREATED_BY like :marker_like)
            """,
            {"marker_like": marker_like},
        )
        cursor.execute("delete from RRL_PICK_FACE where CREATED_BY like :marker_like", {"marker_like": marker_like})
        cursor.execute("delete from RRL_PICK_ROUTE_CELL where CREATED_BY like :marker_like", {"marker_like": marker_like})
        cursor.execute("delete from RRL_PICK_ROUTE where CREATED_BY like :marker_like", {"marker_like": marker_like})
        cursor.execute("delete from RRL_ARTICULS where ACTICUL like :marker_like", {"marker_like": marker_like})
        connection.commit()


def count_load_rows() -> dict[str, int]:
    with connect() as connection:
        cursor = connection.cursor()
        marker_like = f"{LOAD_PREFIX}-%"
        return {
            "waves": count(cursor, "RRL_PICK_WAVE", "CREATED_BY like :marker_like", marker_like=marker_like),
            "plans": count(cursor, "RRL_PICK_PLAN", "CREATED_BY like :marker_like", marker_like=marker_like),
            "warehouse_tasks": count(cursor, "RRL_WAREHOUSE_TASK", "CREATED_BY like :marker_like", marker_like=marker_like),
        }


def build_report(state: LoadState, diagnostics: dict[str, int], elapsed_s: float, args: argparse.Namespace) -> dict[str, Any]:
    metrics = state.metrics
    failed = [m for m in metrics if not m.ok]
    by_endpoint: dict[str, dict[str, Any]] = {}
    for endpoint in sorted({m.endpoint for m in metrics}):
        values = [m.elapsed_ms for m in metrics if m.endpoint == endpoint]
        by_endpoint[endpoint] = summarize(values)
    return {
        "run_prefix": state.run_prefix,
        "waves": args.waves,
        "orders_per_wave": args.orders_per_wave,
        "concurrency": args.concurrency,
        "execute_tasks": args.execute_tasks,
        "replenishment_method": args.replenishment_method,
        "auto_minimax_trigger": args.auto_minimax_trigger,
        "shelf_life_scenario": args.shelf_life_scenario,
        "dynamic_pick_faces": args.dynamic_pick_faces,
        "drain_replenishment_queue": args.drain_replenishment_queue,
        "elapsed_s": round(elapsed_s, 3),
        "request_count": len(metrics),
        "failed_request_count": len(failed),
        "diagnostics": diagnostics,
        "latency_ms": by_endpoint,
        "errors": [m.__dict__ for m in failed[:10]],
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


def duplicate_warehouse_tasks(cursor: oracledb.Cursor, run_prefix: str) -> int:
    cursor.execute(
        """
        select count(*)
          from (
            select SOURCE_TASK_ID, count(*) CNT
              from RRL_WAREHOUSE_TASK
             where TASK_SOURCE = 'WAVE'
               and TASK_TYPE = 'REPLENISHMENT'
               and SOURCE_DOC_ID in (
                 select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY = :marker
               )
             group by SOURCE_TASK_ID
            having count(*) > 1
          )
        """,
        {"marker": run_prefix},
    )
    return int(cursor.fetchone()[0])


def duplicate_source_reservations(cursor: oracledb.Cursor, run_prefix: str) -> int:
    cursor.execute(
        """
        select count(*)
          from (
            select UID_PALLET, CELL, count(*) CNT
              from RRL_STOCK_RESERVATION
             where CREATED_BY = :marker
               and RESERVATION_DOMAIN = 'WAVE'
               and SOURCE_DOC_TYPE = 'PICK_WAVE'
               and RESERVATION_KIND = 'HARD'
               and STATUS in ('ACTIVE', 'ALLOCATED', 'PICKING')
             group by UID_PALLET, CELL
            having count(*) > 1
          )
        """,
        {"marker": run_prefix},
    )
    return int(cursor.fetchone()[0])


def count(cursor: oracledb.Cursor, table: str, where_sql: str, **params: Any) -> int:
    cursor.execute(f"select count(*) from {table} where {where_sql}", params)
    return int(cursor.fetchone()[0])


def call_number(cursor: oracledb.Cursor, block: str, params: dict[str, Any]) -> int:
    result = cursor.var(oracledb.NUMBER)
    cursor.execute(block, {"result": result, **params})
    return int(result.getvalue())


def next_sequence(cursor: oracledb.Cursor, sequence_name: str) -> int:
    cursor.execute(f"select {sequence_name}.nextval from dual")
    return int(cursor.fetchone()[0])


def connect() -> oracledb.Connection:
    return oracledb.connect(
        user=os.getenv("WMS_ORACLE_USER", "RABAEV"),
        password=os.getenv("WMS_ORACLE_PASSWORD", "RABAEVWMS"),
        dsn=os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"),
    )


def random_suffix(length: int) -> str:
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def normalize_endpoint(method: str, path: str) -> str:
    return f"{method} {path.split('?', 1)[0]}"


if __name__ == "__main__":
    main()
