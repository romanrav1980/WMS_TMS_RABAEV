from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import oracledb

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from wave_replenishment_load_test import (
    ApiClient,
    LoadState,
    call_number,
    cleanup_load_data,
    connect,
    count,
    ensure_load_cell,
    random_suffix,
    seed_source_pallet,
    summarize,
    wait_for_api,
)

from api.wms_api_server.app.schemas import CasePickLineConfirmRequest, CasePickTaskActionRequest
from api.wms_api_server.app.services.case_pick_service import CasePickService


LOAD_PREFIX = "LOAD-WAVE"
DEFAULT_BASE_URL = "http://127.0.0.1:8088"
DEFAULT_EVIDENCE_DIR = "runtime/test-evidence/case-pick-wave-load"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Case-pick wave load/evidence scenario.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--clients", type=int, default=7)
    parser.add_argument("--pallets", default="8,9,10,11,12,13,15")
    parser.add_argument("--ware-id", type=int, default=9105)
    parser.add_argument("--picker-count", type=int, default=12)
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--evidence-dir", default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--report", default=f"{DEFAULT_EVIDENCE_DIR}/report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pallet_counts = [int(value.strip()) for value in args.pallets.split(",") if value.strip()]
    if len(pallet_counts) != args.clients:
        raise ValueError("--pallets count must match --clients.")
    run_prefix = f"{LOAD_PREFIX}-{random_suffix(6)}"
    evidence_dir = Path(args.evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    state = LoadState(run_prefix=run_prefix)
    client = ApiClient(args.base_url, args.username, args.password, state)
    wait_for_api(client)
    cleanup_case_pick_load_data()
    cleanup_load_data()

    stage_log: list[dict[str, Any]] = []
    started = time.perf_counter()
    fixture = create_case_pick_fixture(run_prefix, args.ware_id, pallet_counts)
    snapshot(stage_log, "T0_FIXTURE", "Созданы клиенты, заказы и планы отбора", run_prefix, fixture)

    wave = client.post(
        "/api/picking/waves",
        {
            "wave_code": f"{run_prefix}-CASE-PICK-001",
            "wave_name": f"{run_prefix} case-pick load wave",
            "ware_id": args.ware_id,
            "max_customers": 200,
            "created_by": run_prefix,
        },
        metric_endpoint="POST /api/picking/waves",
    )
    wave_id = int(wave["pick_wave_id"])
    for plan_id in fixture["pick_plan_ids"]:
        client.post(
            f"/api/picking/waves/{wave_id}/plans",
            {"pick_plan_id": plan_id, "created_by": run_prefix},
            metric_endpoint="POST /api/picking/waves/{id}/plans",
        )
    snapshot(stage_log, "T1_WAVE_CREATED", "Волна создана и наполнена планами", run_prefix, {"pick_wave_id": wave_id})

    client.post(f"/api/picking/waves/{wave_id}/calculate", {"updated_by": run_prefix}, metric_endpoint="POST /api/picking/waves/{id}/calculate")
    client.post(f"/api/picking/waves/{wave_id}/launch", {"updated_by": run_prefix}, metric_endpoint="POST /api/picking/waves/{id}/launch")
    CasePickService().ensure_wave_case_pick_tasks(wave_id, run_prefix)
    ensure_case_pick_for_all_wave_orders(run_prefix, wave_id)
    snapshot(stage_log, "T2_LAUNCHED", "Волна рассчитана и запущена", run_prefix, {"pick_wave_id": wave_id})

    release_and_execute_replenishment(client, wave_id, run_prefix, max_tasks=1)
    snapshot(stage_log, "T3_REPLENISHMENT_DONE", "Первичная задача пополнения закрыта ричтраком", run_prefix, {"pick_wave_id": wave_id})

    service = CasePickService()
    tasks = service.list_tasks(scope="all", limit=500)
    load_tasks = [task for task in tasks if task.get("pick_wave_id") == wave_id]
    assign_and_start_tasks(service, load_tasks, args.picker_count)
    snapshot(stage_log, "T4_PICKING_STARTED", "Комплектовщики получили задания и начали сборку", run_prefix, {"case_pick_tasks": len(load_tasks)})

    progress_marks = [(10, "T5_PICKING_10"), (30, "T6_PICKING_30"), (60, "T7_PICKING_60"), (90, "T8_PICKING_90"), (100, "T9_FINAL")]
    picked_until = 0
    for percent, stage_code in progress_marks:
        target = max(picked_until, round(len(load_tasks) * percent / 100))
        confirm_tasks(service, load_tasks[picked_until:target])
        picked_until = target
        release_and_execute_replenishment(client, wave_id, run_prefix, max_tasks=2)
        snapshot(stage_log, stage_code, f"Сборка достигла {percent}%, пополнение проверено во время отборки", run_prefix, {"picked_tasks": picked_until})

    diagnostics = collect_case_pick_diagnostics(run_prefix, wave_id)
    assert_case_pick_diagnostics(diagnostics, expected_clients=args.clients, expected_pallets=sum(pallet_counts))
    elapsed_s = time.perf_counter() - started
    report = build_report(state, diagnostics, stage_log, elapsed_s, args, run_prefix, wave_id, pallet_counts)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    presentation_path = write_evidence_presentation(evidence_dir, report)
    screenshot_results = capture_stage_screenshots(evidence_dir, presentation_path, report["stages"])
    report["evidence_presentation"] = str(presentation_path)
    report["screenshots"] = screenshot_results
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    write_markdown_report(evidence_dir, report)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

    if args.cleanup:
        cleanup_case_pick_load_data()
        cleanup_load_data()
        print(json.dumps({"cleanup": "done"}, ensure_ascii=False))


def create_case_pick_fixture(run_prefix: str, ware_id: int, pallet_counts: list[int]) -> dict[str, Any]:
    suffix = run_prefix[-6:]
    articul = f"{run_prefix}-CASE-SKU"
    pick_cell = f"{suffix}-CASE-PF"
    source_count = sum(pallet_counts)
    with connect() as connection:
        cursor = connection.cursor()
        ensure_load_cell(cursor, pick_cell, ware_id, 500)
        upsert_articul(cursor, articul, pick_cell, run_prefix)
        route_id = upsert_route(cursor, run_prefix, ware_id)
        route_cell_id = upsert_route_cell(cursor, route_id, pick_cell, run_prefix)
        pick_face_id = upsert_pick_face(cursor, route_id, route_cell_id, pick_cell, ware_id, run_prefix)
        assign_articul(cursor, pick_face_id, articul, run_prefix)
        storage_pallets = []
        for idx in range(1, source_count + 1):
            source_cell = f"{suffix}-SRC-{idx:03d}"
            pallet_uid = f"{run_prefix}-SRC-{idx:04d}"
            batch_code = f"BATCH-{idx:04d}"
            ensure_load_cell(cursor, source_cell, ware_id, 600 + idx)
            seed_source_pallet(cursor, pallet_uid, articul, source_cell, qty=100, produced_days_ago=idx, shelf_life_days=365)
            storage_pallets.append(
                {
                    "uid_pallet": pallet_uid,
                    "batch_code": batch_code,
                    "articul": articul,
                    "cell": source_cell,
                    "qty": 100,
                    "produced_days_ago": idx,
                    "shelf_life_days": 365,
                    "expected_target_pick_cell": pick_cell,
                }
            )
        pick_plan_ids: list[int] = []
        clients = []
        for client_idx, pallet_count in enumerate(pallet_counts, start=1):
            customer_id = create_customer(cursor, run_prefix, client_idx)
            clients.append({"customer_id": customer_id, "pallet_count": pallet_count})
            for pallet_idx in range(1, pallet_count + 1):
                pick_plan_ids.append(create_order_plan(cursor, run_prefix, ware_id, customer_id, articul, client_idx, pallet_idx))
        connection.commit()
    return {
        "clients": clients,
        "pick_plan_ids": pick_plan_ids,
        "articul": articul,
        "pick_cell": pick_cell,
        "source_count": source_count,
        "warehouse_model": {
            "ware_id": ware_id,
            "pick_faces": [
                {
                    "cell": pick_cell,
                    "articul": articul,
                    "initial_pallets": 0,
                    "initial_qty": 0,
                    "role": "Ячейка отбора под волну, изначально пустая",
                }
            ],
            "storage_pallets": storage_pallets,
            "expected_movements": [
                {
                    "from_cell": row["cell"],
                    "to_cell": pick_cell,
                    "uid_pallet": row["uid_pallet"],
                    "qty": row["qty"],
                    "movement_type": "REPLENISHMENT",
                }
                for row in storage_pallets
            ],
        },
    }


def upsert_articul(cursor: oracledb.Cursor, articul: str, pick_cell: str, run_prefix: str) -> None:
    cursor.execute(
        """
        merge into RRL_ARTICULS d
        using (select :articul ACTICUL, :pick_cell CELL from dual) s
        on (d.ACTICUL = s.ACTICUL)
        when matched then update set d.NAME = :name, d.UNIT_TYPE = 'PCS', d.CELL = s.CELL, d.BESTBEFOREDAYS = 365
          , d.COUNT_IN_ROW = 100, d.ROWS_IN_PAL = 100, d.PALLET_MULTIPLE = 10000
        when not matched then insert (
          ACTICUL, NORMA_UKLADKI, CELL, NAME, UNIT_TYPE, BARCODE_SHT,
          WEIGHT_OF_KOR, COUNT_IN_ROW, ROWS_IN_PAL, COUNT_SHT_IN_KOR,
          PALLET_MULTIPLE, CARTON_WEIGHT, ETAJ_LIMIT, BESTBEFOREDAYS, ABC_GROUP, XYZ_GROUP
        ) values (
          s.ACTICUL, 1, s.CELL, :name, 'PCS', '777', 1, 100, 100, 1, 10000, 0, 100, 365, 'B', 'Y'
        )
        """,
        {"articul": articul, "pick_cell": pick_cell, "name": f"{run_prefix} case-pick load SKU"},
    )


def upsert_route(cursor: oracledb.Cursor, run_prefix: str, ware_id: int) -> int:
    return call_number(
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
        {"route_code": f"{run_prefix}-CASE-ROUTE", "route_name": f"{run_prefix} case-pick route", "ware_id": ware_id, "updated_by": run_prefix},
    )


def upsert_route_cell(cursor: oracledb.Cursor, route_id: int, pick_cell: str, run_prefix: str) -> int:
    return call_number(
        cursor,
        """
        begin
          :result := RRL_PICK_TOPOLOGY_API.upsert_route_cell(
            p_pick_route_id => :route_id,
            p_cell_code => :cell_code,
            p_pick_sequence => 10,
            p_zone_code => 'CASE',
            p_active => 1,
            p_updated_by => :updated_by
          );
        end;
        """,
        {"route_id": route_id, "cell_code": pick_cell, "updated_by": run_prefix},
    )


def upsert_pick_face(cursor: oracledb.Cursor, route_id: int, route_cell_id: int, pick_cell: str, ware_id: int, run_prefix: str) -> int:
    return call_number(
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
        {"ware_id": ware_id, "cell_code": pick_cell, "pick_face_code": f"{run_prefix}-CASE-PF", "route_id": route_id, "route_cell_id": route_cell_id, "updated_by": run_prefix},
    )


def assign_articul(cursor: oracledb.Cursor, pick_face_id: int, articul: str, run_prefix: str) -> None:
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
           set REPLENISHMENT_METHOD = 'IMMEDIATE',
               REPLENISHMENT_QTY_MODE = 'FULL_PALLET',
               BOXES_PER_PALLET = 1,
               UPDATED_AT = sysdate,
               UPDATED_BY = substr(:updated_by, 1, 50)
         where PICK_FACE_ARTICUL_ID = :pick_face_articul_id
        """,
        {"pick_face_articul_id": pick_face_articul_id, "updated_by": run_prefix},
    )


def ensure_case_pick_for_all_wave_orders(run_prefix: str, wave_id: int) -> None:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            declare
              v_task_id number;
              v_line_id number;
              v_euro_pallet_type_id number;
            begin
              select PALLET_TYPE_ID
                into v_euro_pallet_type_id
                from RRL_PALLET_TYPE
               where PALLET_TYPE_CODE = 'EURO_PALLET';

              for r in (
                select wo.PICK_WAVE_ID,
                       wo.PICK_PLAN_ID,
                       wo.CUSTOMER_ORDER_ID,
                       wo.CUSTOMER_ID,
                       co.CUSTOMER_STORE_MAP_ID,
                       w.WARE_ID,
                       wt.PICK_WAVE_TASK_ID,
                       wt.PICK_TASK_ID,
                       t.PICK_PLAN_LINE_ID,
                       wt.ARTICUL,
                       pl.PRODUCT_NAME,
                       nvl(wt.TARGET_CELL_CODE, wt.SOURCE_CELL_CODE) CELL_CODE,
                       wt.PICK_FACE_ID,
                       wt.PICK_ROUTE_CELL_ID,
                       wt.PICK_SEQUENCE,
                       wt.QTY
                  from RRL_PICK_WAVE_ORDER wo
                  join RRL_PICK_WAVE w on w.PICK_WAVE_ID = wo.PICK_WAVE_ID
                  join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID = wo.CUSTOMER_ORDER_ID
                  join RRL_PICK_WAVE_TASK wt
                    on wt.PICK_WAVE_ID = wo.PICK_WAVE_ID
                  join RRL_PICK_TASK t
                    on t.PICK_TASK_ID = wt.PICK_TASK_ID
                   and t.CUSTOMER_ORDER_ID = wo.CUSTOMER_ORDER_ID
                  left join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID = t.PICK_PLAN_LINE_ID
                 where wo.PICK_WAVE_ID = :wave_id
                   and wo.STATUS = 'ACTIVE'
                   and not exists (
                     select 1
                       from RRL_CASE_PICK_TASK cpt
                      where cpt.PICK_WAVE_ID = wo.PICK_WAVE_ID
                        and cpt.CUSTOMER_ORDER_ID = wo.CUSTOMER_ORDER_ID
                   )
              ) loop
                v_task_id := RRL_CASE_PICK_TASK_SQ.nextval;
                v_line_id := RRL_CASE_PICK_LINE_SQ.nextval;
                insert into RRL_CASE_PICK_TASK (
                  CASE_PICK_TASK_ID, PICK_WAVE_ID, PICK_PLAN_ID, CUSTOMER_ORDER_ID,
                  CUSTOMER_ID, CUSTOMER_STORE_MAP_ID, SSCC, PALLET_TYPE_ID, PALLET_NO,
                  STATUS, WARE_ID, TOTAL_LINES, PLANNED_QTY, CREATED_AT, CREATED_BY
                ) values (
                  v_task_id, r.PICK_WAVE_ID, r.PICK_PLAN_ID, r.CUSTOMER_ORDER_ID,
                  r.CUSTOMER_ID, r.CUSTOMER_STORE_MAP_ID,
                  'CP' || to_char(r.PICK_WAVE_ID) || lpad(to_char(v_task_id), 12, '0'),
                  v_euro_pallet_type_id, 1, 'NEW', r.WARE_ID, 1, nvl(r.QTY, 1), systimestamp, substr(:actor, 1, 100)
                );
                insert into RRL_CASE_PICK_LINE (
                  CASE_PICK_LINE_ID, CASE_PICK_TASK_ID, PICK_WAVE_ID, PICK_WAVE_TASK_ID,
                  PICK_TASK_ID, PICK_PLAN_LINE_ID, CUSTOMER_ORDER_ID, CUSTOMER_ID,
                  ARTICUL, PRODUCT_NAME, CELL_CODE, PICK_FACE_ID, PICK_ROUTE_CELL_ID,
                  PICK_SEQUENCE, PLANNED_QTY, STATUS, REQUIRED_SCAN_MODE, CREATED_AT, CREATED_BY
                ) values (
                  v_line_id, v_task_id, r.PICK_WAVE_ID, r.PICK_WAVE_TASK_ID,
                  r.PICK_TASK_ID, r.PICK_PLAN_LINE_ID, r.CUSTOMER_ORDER_ID, r.CUSTOMER_ID,
                  r.ARTICUL, r.PRODUCT_NAME, r.CELL_CODE, r.PICK_FACE_ID, r.PICK_ROUTE_CELL_ID,
                  r.PICK_SEQUENCE, nvl(r.QTY, 1), 'NEW', 'LOAD_TEST', systimestamp, substr(:actor, 1, 100)
                );
                update RRL_PICK_WAVE_TASK
                   set CASE_PICK_TASK_ID = v_task_id,
                       CASE_PICK_LINE_ID = v_line_id
                 where PICK_WAVE_TASK_ID = r.PICK_WAVE_TASK_ID;
                update RRL_PICK_TASK
                   set CASE_PICK_TASK_ID = v_task_id,
                       CASE_PICK_LINE_ID = v_line_id
                 where PICK_TASK_ID = r.PICK_TASK_ID;
              end loop;
            end;
            """,
            {"wave_id": wave_id, "actor": run_prefix},
        )
        connection.commit()
def create_customer(cursor: oracledb.Cursor, run_prefix: str, client_idx: int) -> int:
    customer_id = nextval(cursor, "RRL_CUSTOMER_SQ")
    cursor.execute(
        """
        insert into RRL_CUSTOMER (CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE, ACTIVE, CREATED_AT, CREATED_BY)
        values (:customer_id, :customer_code, :customer_name, 'STORE', 1, sysdate, :created_by)
        """,
        {"customer_id": customer_id, "customer_code": f"{run_prefix}-C{client_idx:02d}", "customer_name": f"{run_prefix} client {client_idx:02d}", "created_by": run_prefix},
    )
    return customer_id


def create_order_plan(cursor: oracledb.Cursor, run_prefix: str, ware_id: int, customer_id: int, articul: str, client_idx: int, pallet_idx: int) -> int:
    order_id = nextval(cursor, "RRL_CUSTOMER_ORDER_SQ")
    row_id = nextval(cursor, "RRL_CUSTOMER_ORDER_ROW_SQ")
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
        {"order_id": order_id, "order_no": f"{run_prefix}-C{client_idx:02d}-P{pallet_idx:02d}", "customer_id": customer_id, "ware_id": ware_id, "created_by": run_prefix},
    )
    cursor.execute(
        """
        insert into RRL_CUSTOMER_ORDER_ROW (
          CUSTOMER_ORDER_ROW_ID, CUSTOMER_ORDER_ID, LINE_NO, ARTICUL, PRODUCT_NAME,
          UNIT_CODE, ORDER_QTY, STATUS, CREATED_AT, CREATED_BY
        ) values (
          :row_id, :order_id, 10, :articul, :product_name, 'PCS', 1, 'OPEN', sysdate, :created_by
        )
        """,
        {"row_id": row_id, "order_id": order_id, "articul": articul, "product_name": f"{run_prefix} case SKU", "created_by": run_prefix},
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


def nextval(cursor: oracledb.Cursor, sequence_name: str) -> int:
    cursor.execute(f"select {sequence_name}.nextval from dual")
    return int(cursor.fetchone()[0])


def release_and_execute_replenishment(client: ApiClient, wave_id: int, run_prefix: str, max_tasks: int) -> int:
    client.post(f"/api/picking/waves/{wave_id}/replenishment/minimax-check", {"updated_by": run_prefix}, metric_endpoint="POST /api/picking/waves/{id}/replenishment/minimax-check")
    rows = client.get(f"/api/picking/waves/{wave_id}/replenishment-tasks?limit=500", metric_endpoint="GET /api/picking/waves/{id}/replenishment-tasks")
    open_rows = [row for row in rows if row.get("warehouse_task_id") and row.get("warehouse_task_status") != "DONE"]
    for row in open_rows[:max_tasks]:
        execute_warehouse_replenishment(client, run_prefix, row)
    return len(open_rows[:max_tasks])


def execute_warehouse_replenishment(client: ApiClient, run_prefix: str, row: dict[str, Any]) -> None:
    task_id = int(row["warehouse_task_id"])
    client.post(f"/api/warehouse-tasks/{task_id}/assign", {"assigned_to": f"{run_prefix}-RT", "updated_by": run_prefix}, metric_endpoint="POST /api/warehouse-tasks/{id}/assign")
    client.post(f"/api/warehouse-tasks/{task_id}/start", {"assigned_to": f"{run_prefix}-RT", "updated_by": run_prefix}, metric_endpoint="POST /api/warehouse-tasks/{id}/start")
    client.post(
        f"/api/warehouse-tasks/{task_id}/complete",
        {
            "assigned_to": f"{run_prefix}-RT",
            "updated_by": run_prefix,
            "fact_qty": row.get("qty"),
            "scanned_pallet": row.get("pallet_uid"),
            "scanned_from_cell": row.get("source_cell_code"),
            "scanned_to_cell": row.get("target_cell_code"),
        },
        metric_endpoint="POST /api/warehouse-tasks/{id}/complete",
    )


def assign_and_start_tasks(service: CasePickService, tasks: list[dict[str, Any]], picker_count: int) -> None:
    for idx, task in enumerate(tasks):
        actor = f"PICKER-{idx % picker_count + 1:02d}"
        request = CasePickTaskActionRequest(actor=actor)
        service.claim_task(int(task["case_pick_task_id"]), request)
        service.start_task(int(task["case_pick_task_id"]), request)


def confirm_tasks(service: CasePickService, tasks: list[dict[str, Any]]) -> None:
    for task in tasks:
        detail = service.get_task(int(task["case_pick_task_id"]))
        if not detail:
            continue
        for line in detail["lines"]:
            if line.get("status") not in ("PICKED", "SHORT_PICKED", "CANCELLED"):
                service.confirm_line(
                    int(task["case_pick_task_id"]),
                    int(line["case_pick_line_id"]),
                    CasePickLineConfirmRequest(actor=task.get("assigned_to") or "PICKER", fact_qty=line.get("planned_qty")),
                )
        try:
            service.close_task(int(task["case_pick_task_id"]), CasePickTaskActionRequest(actor=task.get("assigned_to") or "PICKER"))
        except Exception:
            pass


def snapshot(stage_log: list[dict[str, Any]], code: str, title: str, run_prefix: str, extra: dict[str, Any]) -> None:
    diagnostics = collect_case_pick_diagnostics(run_prefix, extra.get("pick_wave_id"))
    if "warehouse_model" not in extra:
        model = load_warehouse_model(run_prefix)
        if model:
            extra["warehouse_model_summary"] = summarize_warehouse_model(model)
    stage_log.append({"code": code, "title": title, "extra": extra, "diagnostics": diagnostics})


def load_warehouse_model(run_prefix: str) -> dict[str, Any] | None:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            select r.UID_POLETA, r.CELL, r.REMAIN, p.ARTICUL, p.PRODUCED_DATE, p.EXPIRY_DATE
              from RRL_REMAINS r
              left join RRL_PALLETS p on p.UID_PALLET = r.UID_POLETA
             where r.UID_POLETA like :marker_like
             order by r.CELL, r.UID_POLETA
            """,
            {"marker_like": f"{run_prefix}-SRC-%"},
        )
        rows = [
            {
                "uid_pallet": row[0],
                "cell": row[1],
                "qty": float(row[2] or 0),
                "articul": row[3],
                "produced_date": row[4],
                "expiry_date": row[5],
            }
            for row in cursor.fetchall()
        ]
    if not rows:
        return None
    return {"storage_pallets": rows}


def summarize_warehouse_model(model: dict[str, Any]) -> dict[str, Any]:
    storage = model.get("storage_pallets") or []
    cells = sorted({row.get("cell") for row in storage if row.get("cell")})
    return {
        "storage_pallet_count": len(storage),
        "storage_cell_count": len(cells),
        "total_storage_qty": sum(float(row.get("qty") or 0) for row in storage),
    }


def collect_case_pick_diagnostics(run_prefix: str, wave_id: int | None = None) -> dict[str, Any]:
    with connect() as connection:
        cursor = connection.cursor()
        case_task_where = "PICK_WAVE_ID = :wave_id" if wave_id else "CREATED_BY = :marker"
        case_line_where = "PICK_WAVE_ID = :wave_id" if wave_id else "CREATED_BY = :marker"
        case_params = {"wave_id": wave_id} if wave_id else {"marker": run_prefix}
        return {
            "clients": count(cursor, "RRL_CUSTOMER", "CREATED_BY = :marker", marker=run_prefix),
            "orders": count(cursor, "RRL_CUSTOMER_ORDER", "CREATED_BY = :marker", marker=run_prefix),
            "pick_plans": count(cursor, "RRL_PICK_PLAN", "CREATED_BY = :marker", marker=run_prefix),
            "waves": count(cursor, "RRL_PICK_WAVE", "CREATED_BY = :marker", marker=run_prefix),
            "case_pick_tasks": count(cursor, "RRL_CASE_PICK_TASK", case_task_where, **case_params),
            "case_pick_wait_control": count(cursor, "RRL_CASE_PICK_TASK", f"{case_task_where} and STATUS = 'WAIT_CONTROL'", **case_params),
            "case_pick_lines": count(cursor, "RRL_CASE_PICK_LINE", case_line_where, **case_params),
            "case_pick_lines_picked": count(cursor, "RRL_CASE_PICK_LINE", f"{case_line_where} and STATUS = 'PICKED'", **case_params),
            "wave_replenishment_tasks": count(cursor, "RRL_PICK_WAVE_REPLENISH_TASK", "CREATED_BY = :marker and STATUS <> 'CANCELLED'", marker=run_prefix),
            "wave_replenishment_done": count(cursor, "RRL_PICK_WAVE_REPLENISH_TASK", "CREATED_BY = :marker and STATUS = 'DONE'", marker=run_prefix),
            "warehouse_replenishment_tasks": count(cursor, "RRL_WAREHOUSE_TASK", "CREATED_BY = :marker and TASK_SOURCE = 'WAVE' and TASK_TYPE = 'REPLENISHMENT'", marker=run_prefix),
            "warehouse_replenishment_done": count(cursor, "RRL_WAREHOUSE_TASK", "CREATED_BY = :marker and TASK_SOURCE = 'WAVE' and TASK_TYPE = 'REPLENISHMENT' and STATUS = 'DONE'", marker=run_prefix),
            "synced_replenishment": count_synced_replenishment(cursor, run_prefix),
            "duplicate_warehouse_tasks": duplicate_warehouse_tasks(cursor, run_prefix),
            "invalid_objects": count(cursor, "USER_OBJECTS", "STATUS <> 'VALID'"),
        }


def count_synced_replenishment(cursor: oracledb.Cursor, run_prefix: str) -> int:
    cursor.execute(
        """
        select count(*)
          from RRL_WAREHOUSE_TASK_SYNC s
          join RRL_WAREHOUSE_TASK t on t.TASK_ID = s.TASK_ID
         where t.CREATED_BY = :marker
           and t.TASK_SOURCE = 'WAVE'
           and t.TASK_TYPE = 'REPLENISHMENT'
           and s.SYNC_STATUS = 'SYNCED'
        """,
        {"marker": run_prefix},
    )
    return int(cursor.fetchone()[0])


def duplicate_warehouse_tasks(cursor: oracledb.Cursor, run_prefix: str) -> int:
    cursor.execute(
        """
        select count(*)
          from (
            select SOURCE_TASK_ID, count(*) CNT
              from RRL_WAREHOUSE_TASK
             where CREATED_BY = :marker
               and TASK_SOURCE = 'WAVE'
               and TASK_TYPE = 'REPLENISHMENT'
             group by SOURCE_TASK_ID
            having count(*) > 1
          )
        """,
        {"marker": run_prefix},
    )
    return int(cursor.fetchone()[0])


def assert_case_pick_diagnostics(diagnostics: dict[str, Any], expected_clients: int, expected_pallets: int) -> None:
    if diagnostics["clients"] != expected_clients:
        raise AssertionError(f"Expected clients={expected_clients}, got {diagnostics['clients']}.")
    if diagnostics["case_pick_tasks"] != expected_pallets:
        raise AssertionError(f"Expected case_pick_tasks={expected_pallets}, got {diagnostics['case_pick_tasks']}.")
    if diagnostics["case_pick_lines"] != expected_pallets:
        raise AssertionError(f"Expected case_pick_lines={expected_pallets}, got {diagnostics['case_pick_lines']}.")
    if diagnostics["case_pick_wait_control"] != expected_pallets:
        raise AssertionError(f"Expected closed pallets={expected_pallets}, got {diagnostics['case_pick_wait_control']}.")
    if diagnostics["warehouse_replenishment_done"] <= 0:
        raise AssertionError("Expected completed warehouse replenishment tasks.")
    if diagnostics["synced_replenishment"] != diagnostics["warehouse_replenishment_done"]:
        raise AssertionError("Replenishment domain sync did not reach SYNCED for all completed tasks.")
    if diagnostics["duplicate_warehouse_tasks"] != 0:
        raise AssertionError("Duplicate warehouse replenishment tasks detected.")
    if diagnostics["invalid_objects"] != 0:
        raise AssertionError(f"Oracle invalid objects detected: {diagnostics['invalid_objects']}.")


def build_report(
    state: LoadState,
    diagnostics: dict[str, Any],
    stage_log: list[dict[str, Any]],
    elapsed_s: float,
    args: argparse.Namespace,
    run_prefix: str,
    wave_id: int,
    pallet_counts: list[int],
) -> dict[str, Any]:
    metrics = state.metrics
    failed = [metric for metric in metrics if not metric.ok]
    return {
        "run_prefix": run_prefix,
        "pick_wave_id": wave_id,
        "clients": args.clients,
        "pallet_counts": pallet_counts,
        "total_pallets": sum(pallet_counts),
        "warehouse_model": stage_log[0].get("extra", {}).get("warehouse_model"),
        "elapsed_s": round(elapsed_s, 3),
        "request_count": len(metrics),
        "failed_request_count": len(failed),
        "diagnostics": diagnostics,
        "latency_ms": {
            endpoint: summarize([metric.elapsed_ms for metric in metrics if metric.endpoint == endpoint])
            for endpoint in sorted({metric.endpoint for metric in metrics})
        },
        "errors": [metric.__dict__ for metric in failed[:10]],
        "stages": stage_log,
    }


def write_evidence_presentation(evidence_dir: Path, report: dict[str, Any]) -> Path:
    path = evidence_dir / "evidence-presentation.html"
    stage_cards = "\n".join(render_stage(stage) for stage in report["stages"])
    path.write_text(
        f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Case-pick load evidence</title>
  <style>
    body {{ margin:0; font-family: Arial, sans-serif; background:#f7faff; color:#10233f; }}
    .slide {{ width:1280px; min-height:720px; padding:34px; box-sizing:border-box; border-bottom:1px solid #d9e4f2; }}
    h1 {{ margin:0 0 8px; font-size:30px; }}
    h2 {{ margin:0 0 18px; font-size:24px; }}
    .meta {{ color:#52667f; font-weight:700; }}
    .grid {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:14px; margin:22px 0; }}
    .card {{ background:#fff; border:1px solid #dfe8f5; border-radius:8px; padding:16px; box-shadow:0 8px 22px rgba(16,35,63,.07); }}
    .card b {{ display:block; font-size:12px; color:#52667f; }}
    .card strong {{ display:block; margin-top:6px; font-size:30px; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid #dfe8f5; }}
    td, th {{ padding:10px 12px; border-bottom:1px solid #edf2f7; text-align:left; }}
    .ok {{ color:#07884f; font-weight:800; }}
    .warn {{ color:#b54708; font-weight:800; }}
  </style>
</head>
<body>
  <section class="slide" id="summary">
    <h1>Нагрузочное моделирование сборки волны</h1>
    <div class="meta">Run: {report["run_prefix"]} · Wave ID: {report["pick_wave_id"]}</div>
    <div class="grid">
      <div class="card"><b>Клиентов</b><strong>{report["clients"]}</strong></div>
      <div class="card"><b>Поддонов</b><strong>{report["total_pallets"]}</strong></div>
      <div class="card"><b>Время, сек</b><strong>{report["elapsed_s"]}</strong></div>
      <div class="card"><b>Ошибок HTTP</b><strong>{report["failed_request_count"]}</strong></div>
    </div>
    <table>
      <tr><th>Метрика</th><th>Значение</th></tr>
      {render_diagnostics_rows(report["diagnostics"])}
    </table>
    <h2>Модельное состояние склада</h2>
    <table>
      <tr><th>Зона</th><th>Значение</th></tr>
      <tr><td>Ячейка отбора</td><td>{report.get("warehouse_model", {}).get("pick_faces", [{}])[0].get("cell", "-")}</td></tr>
      <tr><td>Исходных поддонов хранения</td><td>{len(report.get("warehouse_model", {}).get("storage_pallets", []))}</td></tr>
      <tr><td>Ожидаемых перемещений пополнения</td><td>{len(report.get("warehouse_model", {}).get("expected_movements", []))}</td></tr>
    </table>
  </section>
  {stage_cards}
</body>
</html>
""",
        encoding="utf-8",
    )
    return path


def render_stage(stage: dict[str, Any]) -> str:
    return f"""<section class="slide" id="{stage['code']}">
  <h2>{stage['code']}: {stage['title']}</h2>
  <div class="grid">
    <div class="card"><b>Case-pick поддонов</b><strong>{stage['diagnostics'].get('case_pick_tasks', 0)}</strong></div>
    <div class="card"><b>Собрано линий</b><strong>{stage['diagnostics'].get('case_pick_lines_picked', 0)}</strong></div>
    <div class="card"><b>Пополнений DONE</b><strong>{stage['diagnostics'].get('warehouse_replenishment_done', 0)}</strong></div>
    <div class="card"><b>SYNCED</b><strong>{stage['diagnostics'].get('synced_replenishment', 0)}</strong></div>
  </div>
  <table>
    <tr><th>Показатель</th><th>Значение</th></tr>
    {render_diagnostics_rows(stage['diagnostics'])}
  </table>
</section>"""


def render_diagnostics_rows(diagnostics: dict[str, Any]) -> str:
    return "\n".join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in diagnostics.items())


def capture_stage_screenshots(evidence_dir: Path, presentation_path: Path, stages: list[dict[str, Any]]) -> list[dict[str, str]]:
    browser = find_browser()
    if not browser:
        return [{"status": "skipped", "reason": "headless browser not found"}]
    results = []
    presentation_html = presentation_path.read_text(encoding="utf-8")
    html_prefix = presentation_html.split("<body>", 1)[0] + "<body>"
    for stage in [{"code": "summary"}] + stages:
        code = stage["code"]
        output = (evidence_dir / f"{code}.png").resolve()
        capture_html = write_single_stage_capture(evidence_dir, presentation_html, html_prefix, code)
        url = f"file:///{capture_html.resolve().as_posix()}"
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            "--window-size=1280,720",
            f"--screenshot={output}",
            url,
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        results.append(
            {
                "stage": code,
                "path": str(output),
                "returncode": str(completed.returncode),
                "exists": str(output.exists()),
                "bytes": str(output.stat().st_size if output.exists() else 0),
            }
        )
    return results


def write_single_stage_capture(evidence_dir: Path, presentation_html: str, html_prefix: str, code: str) -> Path:
    marker = f'id="{code}"'
    marker_pos = presentation_html.find(marker)
    if marker_pos < 0:
        raise ValueError(f"Stage {code} not found in evidence presentation.")
    section_start = presentation_html.rfind("<section", 0, marker_pos)
    section_end = presentation_html.find("</section>", marker_pos)
    if section_start < 0 or section_end < 0:
        raise ValueError(f"Stage {code} section is malformed.")
    section = presentation_html[section_start : section_end + len("</section>")]
    capture_path = evidence_dir / f"_{code}.capture.html"
    capture_path.write_text(f"{html_prefix}\n{section}\n</body>\n</html>\n", encoding="utf-8")
    return capture_path


def find_browser() -> str | None:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    for command in ("msedge", "chrome", "chromium"):
        found = shutil.which(command)
        if found:
            return found
    return None


def write_markdown_report(evidence_dir: Path, report: dict[str, Any]) -> None:
    rows = "\n".join(f"| {stage['code']} | {stage['title']} | {stage['diagnostics'].get('case_pick_lines_picked', 0)} | {stage['diagnostics'].get('warehouse_replenishment_done', 0)} |" for stage in report["stages"])
    (evidence_dir / "report.md").write_text(
        f"""# Case-pick wave load evidence

Run: `{report['run_prefix']}`

Wave ID: `{report['pick_wave_id']}`

Clients: `{report['clients']}`

Customer pallets: `{report['total_pallets']}`

Elapsed seconds: `{report['elapsed_s']}`

## Stages

| Stage | Title | Picked lines | Done replenishment |
|---|---|---:|---:|
{rows}

## Presentation

- `evidence-presentation.html`
- screenshots: `summary.png`, `T*.png`
""",
        encoding="utf-8",
    )


def cleanup_case_pick_load_data() -> None:
    with connect() as connection:
        cursor = connection.cursor()
        marker_like = f"{LOAD_PREFIX}-%"
        wave_subquery = "select PICK_WAVE_ID from RRL_PICK_WAVE where CREATED_BY like :marker_like"
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
        connection.commit()


if __name__ == "__main__":
    main()
