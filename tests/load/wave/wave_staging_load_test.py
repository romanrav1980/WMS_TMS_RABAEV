from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import oracledb

from wave_replenishment_load_test import (
    ApiClient,
    LoadState,
    call_number,
    cleanup_load_data,
    connect,
    count,
    ensure_load_cell,
    next_sequence,
    normalize_endpoint,
    random_suffix,
    seed_source_pallet,
    summarize,
    wait_for_api,
)


LOAD_PREFIX = "LOAD-WAVE"
DEFAULT_BASE_URL = "http://127.0.0.1:8088"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave loading-zone staging PICKING_MOVE load smoke.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--waves", type=int, default=1)
    parser.add_argument("--full-pallet-articuls", type=int, default=1)
    parser.add_argument("--mixed-case-pick", action="store_true")
    parser.add_argument("--repeat-release", action="store_true")
    parser.add_argument("--concurrent-release-workers", type=int, default=1)
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--report", default="tests/load/wave/staging_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.waves < 1:
        raise ValueError("--waves must be at least 1.")
    if args.full_pallet_articuls < 1:
        raise ValueError("--full-pallet-articuls must be at least 1.")
    if args.concurrent_release_workers < 1:
        raise ValueError("--concurrent-release-workers must be at least 1.")
    run_prefix = f"{LOAD_PREFIX}-{random_suffix(6)}"
    state = LoadState(run_prefix=run_prefix)
    client = ApiClient(args.base_url, args.username, args.password, state)
    wait_for_api(client)
    cleanup_load_data()

    started = time.perf_counter()
    for wave_idx in range(1, args.waves + 1):
        fixture = create_staging_fixture(run_prefix, wave_idx, args.full_pallet_articuls, args.mixed_case_pick)
        run_staging_wave(client, run_prefix, wave_idx, fixture, args)

    diagnostics = collect_staging_diagnostics(run_prefix)
    assert_staging_diagnostics(
        diagnostics,
        expected_waves=args.waves,
        expected_full_pallets=args.waves * args.full_pallet_articuls,
        expected_case_picks=args.waves if args.mixed_case_pick else 0,
    )
    elapsed_s = time.perf_counter() - started
    report = build_report(state, diagnostics, elapsed_s, args)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.cleanup:
        cleanup_load_data()
        print(json.dumps({"cleanup": "done", "remaining": count_load_rows()}, ensure_ascii=False))


def run_staging_wave(
    client: ApiClient,
    run_prefix: str,
    wave_idx: int,
    fixture: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    wave = client.post(
        "/api/picking/waves",
        {
            "wave_code": f"{run_prefix}-STAGE-{wave_idx:03d}",
            "wave_name": f"{run_prefix} staging wave {wave_idx:03d}",
            "ware_id": fixture["ware_id"],
            "max_customers": 100,
            "created_by": run_prefix,
        },
        metric_endpoint="POST /api/picking/waves",
    )
    wave_id = int(wave["pick_wave_id"])
    for plan in fixture["full_pallet_plans"]:
        client.post(
            f"/api/picking/waves/{wave_id}/plans",
            {"pick_plan_id": plan["pick_plan_id"], "created_by": run_prefix},
            metric_endpoint="POST /api/picking/waves/{id}/plans",
        )
    if args.mixed_case_pick:
        client.post(
            f"/api/picking/waves/{wave_id}/plans",
            {"pick_plan_id": fixture["case_pick_plan_id"], "created_by": run_prefix},
            metric_endpoint="POST /api/picking/waves/{id}/plans",
        )
    client.post(
        f"/api/picking/waves/{wave_id}/calculate",
        {"updated_by": run_prefix},
        metric_endpoint="POST /api/picking/waves/{id}/calculate",
    )
    client.post(
        f"/api/picking/waves/{wave_id}/launch",
        {"updated_by": run_prefix},
        metric_endpoint="POST /api/picking/waves/{id}/launch",
    )
    release_results = run_staging_release_calls(client, wave_id, fixture["staging_cell"], run_prefix, args.concurrent_release_workers)
    released_count = sum(int(result.get("released_count") or 0) for result in release_results)
    if released_count != len(fixture["full_pallet_plans"]):
        raise AssertionError(f"Expected {len(fixture['full_pallet_plans'])} staging tasks, got {release_results}.")
    if args.repeat_release:
        repeated_results = run_staging_release_calls(client, wave_id, fixture["staging_cell"], run_prefix, args.concurrent_release_workers)
        repeated_count = sum(int(result.get("released_count") or 0) for result in repeated_results)
        if repeated_count != 0:
            raise AssertionError(f"Repeated staging release created duplicates: {repeated_results}.")

    tasks = client.get(
        f"/api/picking/waves/{wave_id}/tasks?limit=500",
        metric_endpoint="GET /api/picking/waves/{id}/tasks",
    )
    full_pallet_tasks = [row for row in tasks if row.get("task_type") == "FULL_PALLET"]
    if len(full_pallet_tasks) != len(fixture["full_pallet_plans"]):
        raise AssertionError(f"Expected {len(fixture['full_pallet_plans'])} FULL_PALLET wave tasks, got {tasks}.")
    if not all(row.get("warehouse_task_id") for row in full_pallet_tasks):
        raise AssertionError(f"Some FULL_PALLET wave tasks have no warehouse task: {full_pallet_tasks}.")
    if args.mixed_case_pick:
        case_pick_tasks = [row for row in tasks if row.get("task_type") == "CASE_PICK"]
        if len(case_pick_tasks) != 1:
            raise AssertionError(f"Expected one CASE_PICK wave task in mixed wave, got {tasks}.")
        case_task = case_pick_tasks[0]
        client.post(
            f"/api/picking/waves/{wave_id}/tasks/{case_task['pick_task_id']}/complete",
            {
                "completed_by": run_prefix,
                "scanned_pallet": case_task.get("pallet_uid"),
                "scanned_from_cell": case_task.get("source_cell_code"),
                "scanned_to_cell": case_task.get("target_cell_code"),
            },
            metric_endpoint="POST /api/picking/waves/{id}/tasks/{id}/complete",
        )

    for wave_task in full_pallet_tasks:
        warehouse_task_id = int(wave_task["warehouse_task_id"])
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
                "scanned_pallet": wave_task.get("pallet_uid"),
                "scanned_from_cell": wave_task.get("source_cell_code"),
                "scanned_to_cell": fixture["staging_cell"],
            },
            metric_endpoint="POST /api/warehouse-tasks/{id}/complete",
        )


def run_staging_release_calls(
    client: ApiClient,
    wave_id: int,
    staging_cell: str,
    run_prefix: str,
    workers: int,
) -> list[dict[str, Any]]:
    def release_once() -> dict[str, Any]:
        return client.post(
            f"/api/picking/waves/{wave_id}/staging/release",
            {"to_cell": staging_cell, "updated_by": run_prefix},
            metric_endpoint="POST /api/picking/waves/{id}/staging/release",
        )

    if workers <= 1:
        return [release_once()]
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(release_once) for _ in range(workers)]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def create_staging_fixture(
    run_prefix: str,
    wave_idx: int,
    full_pallet_articuls: int,
    include_case_pick: bool,
) -> dict[str, Any]:
    suffix = run_prefix[-6:]
    ware_id = 9104
    staging_cell = f"{suffix}-W{wave_idx:02d}-LD"
    with connect() as connection:
        cursor = connection.cursor()
        ensure_load_cell(cursor, staging_cell, ware_id, 200 + wave_idx)
        full_pallet_plans = [
            create_full_pallet_plan(cursor, run_prefix, wave_idx, articul_idx, ware_id)
            for articul_idx in range(1, full_pallet_articuls + 1)
        ]
        case_pick_plan_id = create_case_pick_plan(cursor, run_prefix, wave_idx, ware_id) if include_case_pick else None
        connection.commit()
    return {
        "ware_id": ware_id,
        "full_pallet_plans": full_pallet_plans,
        "case_pick_plan_id": case_pick_plan_id,
        "staging_cell": staging_cell,
    }


def create_full_pallet_plan(
    cursor: oracledb.Cursor,
    run_prefix: str,
    wave_idx: int,
    articul_idx: int,
    ware_id: int,
) -> dict[str, Any]:
    suffix = run_prefix[-6:]
    articul = f"{run_prefix}-STAGE-W{wave_idx:02d}-A{articul_idx:02d}"
    source_cell = f"{suffix}-W{wave_idx:02d}-S{articul_idx:02d}"
    uid_pallet = f"{run_prefix}-SRC-W{wave_idx:02d}-A{articul_idx:02d}"
    ensure_load_cell(cursor, source_cell, ware_id, 210 + wave_idx * 10 + articul_idx)
    upsert_articul(cursor, articul, source_cell, run_prefix)
    seed_source_pallet(cursor, uid_pallet, articul, source_cell, qty=10, produced_days_ago=1, shelf_life_days=100)
    pick_plan_id = create_order_plan(
        cursor,
        run_prefix,
        ware_id,
        articul,
        order_qty=10,
        order_suffix=f"W{wave_idx:02d}-A{articul_idx:02d}",
    )
    return {
        "pick_plan_id": pick_plan_id,
        "uid_pallet": uid_pallet,
        "source_cell": source_cell,
        "articul": articul,
    }


def upsert_articul(cursor: oracledb.Cursor, articul: str, source_cell: str, run_prefix: str) -> None:
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
          d.BARCODE_SHT = nvl(d.BARCODE_SHT, '777')
        when not matched then insert (
          ACTICUL, NORMA_UKLADKI, CELL, NAME, UNIT_TYPE, BARCODE_SHT,
          WEIGHT_OF_KOR, COUNT_IN_ROW, ROWS_IN_PAL, COUNT_SHT_IN_KOR,
          PALLET_MULTIPLE, CARTON_WEIGHT, ETAJ_LIMIT, BESTBEFOREDAYS,
          ABC_GROUP, XYZ_GROUP
        ) values (
          s.ACTICUL, 1, s.CELL, :name, 'PCS', '777',
          1, 10, 1, 1, 1, 0, 100, 100, 'B', 'Y'
        )
        """,
        {"articul": articul, "source_cell": source_cell, "name": f"{run_prefix} staging product"},
    )


def create_order_plan(
    cursor: oracledb.Cursor,
    run_prefix: str,
    ware_id: int,
    articul: str,
    order_qty: int,
    order_suffix: str,
) -> int:
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
            "customer_code": f"{run_prefix}-{order_suffix}-C",
            "customer_name": f"{run_prefix} customer {order_suffix}",
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
            "order_no": f"{run_prefix}-{order_suffix}-O",
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
          :product_name, 'PCS', :order_qty, 'OPEN', sysdate, :created_by
        )
        """,
        {
            "row_id": row_id,
            "order_id": order_id,
            "articul": articul,
            "product_name": f"{run_prefix} product {order_suffix}",
            "order_qty": order_qty,
            "created_by": run_prefix,
        },
    )
    return call_number(
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


def create_case_pick_plan(cursor: oracledb.Cursor, run_prefix: str, wave_idx: int, ware_id: int) -> int:
    suffix = run_prefix[-6:]
    articul = f"{run_prefix}-CASE-W{wave_idx:02d}"
    pick_cell = f"{suffix}-W{wave_idx:02d}-PF"
    uid_pallet = f"{run_prefix}-PF-CASE-W{wave_idx:02d}"
    ensure_load_cell(cursor, pick_cell, ware_id, 300 + wave_idx)
    upsert_articul(cursor, articul, pick_cell, run_prefix)
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
            "route_code": f"{run_prefix}-CASE-W{wave_idx:02d}-ROUTE",
            "route_name": f"{run_prefix} case route {wave_idx:02d}",
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
            p_pick_sequence => 20,
            p_zone_code => :zone_code,
            p_active => 1,
            p_updated_by => :updated_by
          );
        end;
        """,
        {
            "route_id": route_id,
            "cell_code": pick_cell,
            "zone_code": "CASE",
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
            "pick_face_code": f"{run_prefix}-CASE-W{wave_idx:02d}-PF",
            "route_id": route_id,
            "route_cell_id": route_cell_id,
            "updated_by": run_prefix,
        },
    )
    call_number(
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
    seed_source_pallet(cursor, uid_pallet, articul, pick_cell, qty=5, produced_days_ago=1, shelf_life_days=100)
    return create_order_plan(
        cursor,
        run_prefix,
        ware_id,
        articul,
        order_qty=1,
        order_suffix=f"CASE-W{wave_idx:02d}",
    )


def collect_staging_diagnostics(run_prefix: str) -> dict[str, int]:
    with connect() as connection:
        cursor = connection.cursor()
        return {
            "waves": count(cursor, "RRL_PICK_WAVE", "CREATED_BY = :marker", marker=run_prefix),
            "full_pallet_wave_tasks_done": count(
                cursor,
                "RRL_PICK_WAVE_TASK",
                "CREATED_BY = :marker and TASK_TYPE = 'FULL_PALLET' and STATUS = 'DONE'",
                marker=run_prefix,
            ),
            "case_pick_wave_tasks": count(
                cursor,
                "RRL_PICK_WAVE_TASK",
                "CREATED_BY = :marker and TASK_TYPE = 'CASE_PICK'",
                marker=run_prefix,
            ),
            "case_pick_wave_tasks_done": count(
                cursor,
                "RRL_PICK_WAVE_TASK",
                "CREATED_BY = :marker and TASK_TYPE = 'CASE_PICK' and STATUS = 'DONE'",
                marker=run_prefix,
            ),
            "warehouse_picking_moves": count(
                cursor,
                "RRL_WAREHOUSE_TASK",
                "CREATED_BY = :marker and TASK_SOURCE = 'WAVE' and TASK_TYPE = 'PICKING_MOVE'",
                marker=run_prefix,
            ),
            "done_warehouse_picking_moves": count(
                cursor,
                "RRL_WAREHOUSE_TASK",
                "CREATED_BY = :marker and TASK_SOURCE = 'WAVE' and TASK_TYPE = 'PICKING_MOVE' and STATUS = 'DONE'",
                marker=run_prefix,
            ),
            "synced_picking_moves": count(
                cursor,
                "RRL_WAREHOUSE_TASK_SYNC",
                """
                TASK_SOURCE = 'WAVE'
                and TASK_TYPE = 'PICKING_MOVE'
                and SYNC_STATUS = 'SYNCED'
                and TASK_ID in (
                  select TASK_ID
                    from RRL_WAREHOUSE_TASK
                   where CREATED_BY = :marker
                     and TASK_SOURCE = 'WAVE'
                     and TASK_TYPE = 'PICKING_MOVE'
                )
                """,
                marker=run_prefix,
            ),
            "duplicate_picking_moves": duplicate_picking_moves(cursor, run_prefix),
            "invalid_objects": count(cursor, "USER_OBJECTS", "STATUS <> 'VALID'"),
        }


def assert_staging_diagnostics(
    diagnostics: dict[str, int],
    expected_waves: int,
    expected_full_pallets: int,
    expected_case_picks: int,
) -> None:
    if diagnostics["waves"] != expected_waves:
        raise AssertionError(f"Expected waves={expected_waves}, got {diagnostics['waves']}.")
    for key in ("full_pallet_wave_tasks_done", "warehouse_picking_moves", "done_warehouse_picking_moves", "synced_picking_moves"):
        if diagnostics[key] != expected_full_pallets:
            raise AssertionError(f"Expected {key}={expected_full_pallets}, got {diagnostics[key]}.")
    if diagnostics["case_pick_wave_tasks"] != expected_case_picks:
        raise AssertionError(f"Expected case_pick_wave_tasks={expected_case_picks}, got {diagnostics['case_pick_wave_tasks']}.")
    if diagnostics["case_pick_wave_tasks_done"] != expected_case_picks:
        raise AssertionError(f"Expected case_pick_wave_tasks_done={expected_case_picks}, got {diagnostics['case_pick_wave_tasks_done']}.")
    if diagnostics["duplicate_picking_moves"] != 0:
        raise AssertionError("Duplicate PICKING_MOVE warehouse tasks detected.")
    if diagnostics["invalid_objects"] != 0:
        raise AssertionError(f"Oracle invalid objects detected: {diagnostics['invalid_objects']}.")


def duplicate_picking_moves(cursor: oracledb.Cursor, run_prefix: str) -> int:
    cursor.execute(
        """
        select count(*)
          from (
            select SOURCE_TASK_ID, count(*) CNT
              from RRL_WAREHOUSE_TASK
             where CREATED_BY = :marker
               and TASK_SOURCE = 'WAVE'
               and TASK_TYPE = 'PICKING_MOVE'
             group by SOURCE_TASK_ID
            having count(*) > 1
          )
        """,
        {"marker": run_prefix},
    )
    return int(cursor.fetchone()[0])


def build_report(state: LoadState, diagnostics: dict[str, int], elapsed_s: float, args: argparse.Namespace) -> dict[str, Any]:
    metrics = state.metrics
    failed = [m for m in metrics if not m.ok]
    return {
        "run_prefix": state.run_prefix,
        "elapsed_s": round(elapsed_s, 3),
        "waves": args.waves,
        "full_pallet_articuls": args.full_pallet_articuls,
        "concurrent_release_workers": args.concurrent_release_workers,
        "request_count": len(metrics),
        "failed_request_count": len(failed),
        "mixed_case_pick": args.mixed_case_pick,
        "repeat_release": args.repeat_release,
        "diagnostics": diagnostics,
        "latency_ms": {
            endpoint: summarize([m.elapsed_ms for m in metrics if m.endpoint == endpoint])
            for endpoint in sorted({m.endpoint for m in metrics})
        },
        "errors": [m.__dict__ for m in failed[:10]],
    }


def count_load_rows() -> dict[str, int]:
    with connect() as connection:
        cursor = connection.cursor()
        marker_like = f"{LOAD_PREFIX}-%"
        return {
            "waves": count(cursor, "RRL_PICK_WAVE", "CREATED_BY like :marker_like", marker_like=marker_like),
            "plans": count(cursor, "RRL_PICK_PLAN", "CREATED_BY like :marker_like", marker_like=marker_like),
            "warehouse_tasks": count(cursor, "RRL_WAREHOUSE_TASK", "CREATED_BY like :marker_like", marker_like=marker_like),
        }


if __name__ == "__main__":
    main()
