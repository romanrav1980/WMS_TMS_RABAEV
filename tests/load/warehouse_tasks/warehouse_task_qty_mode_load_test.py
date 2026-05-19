import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any

import oracledb


def oracle_config() -> dict[str, str]:
    return {
        "user": os.getenv("WMS_ORACLE_USER", "RABAEV"),
        "password": os.getenv("WMS_ORACLE_PASSWORD", "RABAEVWMS"),
        "dsn": os.getenv("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"),
    }


def auth_header() -> str:
    raw = f"{os.getenv('WMS_LOAD_USER', 'admin')}:{os.getenv('WMS_LOAD_PASSWORD', 'admin123')}"
    return "Basic " + base64.b64encode(raw.encode("ascii")).decode("ascii")


def api_post(api_base: str, path: str, payload: dict[str, Any]) -> tuple[int, str]:
    request = urllib.request.Request(
        api_base.rstrip("/") + path,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", auth_header())
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def create_task(marker: str, mode: str, qty: float, source_task_id: int) -> int:
    with oracledb.connect(**oracle_config()) as connection:
        cursor = connection.cursor()
        task_id_var = cursor.var(oracledb.NUMBER)
        cursor.execute(
            """
            begin
              :task_id := RRL_WAREHOUSE_TASK_SQ.nextval;
              insert into RRL_WAREHOUSE_TASK (
                TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_TASK_ID, SOURCE_DOC_TYPE,
                SOURCE_DOC_ID, UID_PALLET, FROM_CELL, TO_CELL, QTY, UNIT_CODE,
                QTY_MODE, PRIORITY, STATUS, CREATED_BY
              ) values (
                :task_id, 'OTHER', 'MANUAL', :source_task_id, 'LOAD_TEST',
                :source_doc_id, :uid_pallet, 'LOAD-A-01', 'LOAD-B-01', :qty,
                :unit_code, :qty_mode, 10, 'PLANNED', :created_by
              );
            end;
            """,
            {
                "task_id": task_id_var,
                "source_task_id": source_task_id,
                "source_doc_id": source_task_id,
                "uid_pallet": f"{marker}-{mode}-{source_task_id}",
                "qty": qty,
                "unit_code": "BOX" if mode == "BOX" else "KG",
                "qty_mode": mode,
                "created_by": marker,
            },
        )
        connection.commit()
        return int(task_id_var.getvalue())


def run_one(api_base: str, marker: str, index: int) -> dict[str, Any]:
    source_base = int(time.time()) * 1000 + index * 10
    box_task_id = create_task(marker, "BOX", 10, source_base + 1)
    pallet_task_id = create_task(marker, "PALLET", 100, source_base + 2)

    status, body = api_post(
        api_base,
        f"/api/warehouse-tasks/{box_task_id}/complete",
        {
            "assigned_to": f"{marker}-DRIVER",
            "updated_by": marker,
            "fact_qty": 4,
            "scanned_pallet": f"{marker}-BOX-{source_base + 1}",
            "scanned_from_cell": "LOAD-A-01",
            "scanned_to_cell": "LOAD-B-01",
        },
    )
    if status != 200:
        raise AssertionError(f"BOX partial failed for {box_task_id}: HTTP {status} {body}")

    status, body = api_post(
        api_base,
        f"/api/warehouse-tasks/{pallet_task_id}/complete",
        {
            "assigned_to": f"{marker}-DRIVER",
            "updated_by": marker,
            "fact_qty": 50,
            "scanned_pallet": f"{marker}-PALLET-{source_base + 2}",
            "scanned_from_cell": "LOAD-A-01",
            "scanned_to_cell": "LOAD-B-01",
        },
    )
    if status != 409:
        raise AssertionError(f"PALLET partial should be rejected for {pallet_task_id}: HTTP {status} {body}")

    return {"box_task_id": box_task_id, "pallet_task_id": pallet_task_id}


def verify(marker: str) -> dict[str, int]:
    with oracledb.connect(**oracle_config()) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            select
              sum(case when QTY_MODE = 'BOX' and STATUS = 'DONE' and QTY = 4 and FACT_QTY = 4 then 1 else 0 end) BOX_DONE,
              sum(case when QTY_MODE = 'BOX' and STATUS = 'PLANNED' and QTY = 6 and PARENT_TASK_ID is not null then 1 else 0 end) BOX_RESIDUAL,
              sum(case when QTY_MODE = 'PALLET' and STATUS = 'PLANNED' and FACT_QTY is null then 1 else 0 end) PALLET_OPEN
            from RRL_WAREHOUSE_TASK
            where CREATED_BY in (:marker, :driver_marker)
            """,
            {"marker": marker, "driver_marker": f"{marker}-DRIVER"},
        )
        row = cursor.fetchone()
        return {
            "box_done": int(row[0] or 0),
            "box_residual": int(row[1] or 0),
            "pallet_open": int(row[2] or 0),
        }


def cleanup(marker: str) -> int:
    with oracledb.connect(**oracle_config()) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "delete from RRL_WAREHOUSE_TASK where CREATED_BY in (:marker, :driver_marker)",
            {"marker": marker, "driver_marker": f"{marker}-DRIVER"},
        )
        deleted = cursor.rowcount
        connection.commit()
        return int(deleted or 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-base", default=os.getenv("WMS_API_BASE_URL", "http://127.0.0.1:8088"))
    parser.add_argument("--iterations", type=int, default=4)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    marker = "LOAD-QTYMODE-" + datetime.now().strftime("%Y%m%d%H%M%S")
    started = time.perf_counter()
    try:
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = [pool.submit(run_one, args.api_base, marker, index) for index in range(args.iterations)]
            for future in as_completed(futures):
                future.result()
        summary = verify(marker)
        expected = args.iterations
        if summary != {"box_done": expected, "box_residual": expected, "pallet_open": expected}:
            raise AssertionError(f"Unexpected summary: {summary}, expected {expected} each.")
        print(json.dumps({"marker": marker, "elapsed_sec": round(time.perf_counter() - started, 3), **summary}, ensure_ascii=False))
    finally:
        if args.cleanup:
            print(json.dumps({"cleanup_deleted": cleanup(marker)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
