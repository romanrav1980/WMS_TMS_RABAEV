import argparse
import base64
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date


RAW_ARTICUL = "RM-MEAT-BEEF-FROZ-01"
TO_WARE_ID = 9102
TO_CELL = "MES_PROD"


def main() -> int:
    parser = argparse.ArgumentParser(description="MES raw supply reservation smoke/load test.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    parser.add_argument("--user", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--orders", type=int, default=12)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    client = Client(args.base_url, args.user, args.password)
    client.get("/health", auth=False)

    suffix = time.strftime("%Y%m%d%H%M%S")
    started = time.perf_counter()

    bom_id, target = create_bom(client, suffix)
    created_orders: list[int] = []
    created_tasks: list[int] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=max(args.workers, 1)) as pool:
        futures = [
            pool.submit(create_and_release_order, client, i, bom_id, target, suffix)
            for i in range(1, args.orders + 1)
        ]
        for future in as_completed(futures):
            try:
                order_id, tasks = future.result()
                created_orders.append(order_id)
                created_tasks.extend(
                    int(task["task_id"])
                    for task in tasks
                    if task.get("task_status") == "PLANNED"
                )
            except Exception as exc:
                errors.append(str(exc))

    if errors:
        raise AssertionError("\n".join(errors[:10]))

    confirm_bom_id, confirm_target = create_bom(client, suffix + "C")
    confirm_order_id, confirm_tasks = create_and_release_order(
        client,
        999,
        confirm_bom_id,
        confirm_target,
        suffix,
    )
    confirm_task = next(task for task in confirm_tasks if task.get("task_status") == "PLANNED")
    confirm_warehouse_tasks = client.get(
        f"/api/warehouse-tasks?production_order_id={confirm_order_id}&task_type=RAW_TO_PRODUCTION&limit=20"
    )
    confirm_warehouse_task = next(
        task
        for task in confirm_warehouse_tasks
        if int(task.get("source_task_id") or 0) == int(confirm_task["task_id"])
    )
    complete_payload = {
        "assigned_to": "raw-supply-smoke",
        "scanned_pallet": confirm_warehouse_task.get("uid_pallet") or confirm_warehouse_task.get("sscc"),
        "scanned_from_cell": confirm_warehouse_task.get("from_cell"),
        "scanned_to_cell": confirm_warehouse_task.get("to_cell"),
    }
    client.post(f"/api/warehouse-tasks/{confirm_warehouse_task['task_id']}/assign", complete_payload)
    client.post(f"/api/warehouse-tasks/{confirm_warehouse_task['task_id']}/start", complete_payload)
    client.post(f"/api/warehouse-tasks/{confirm_warehouse_task['task_id']}/complete", complete_payload)
    confirmed_task = client.get(f"/api/mes/raw-transfer-tasks/{confirm_task['task_id']}")
    if confirmed_task.get("task_status") != "DONE":
        raise AssertionError(f"Expected confirmed task DONE, got {confirmed_task.get('task_status')}")
    confirmed_warehouse_tasks = client.get(
        f"/api/warehouse-tasks?production_order_id={confirm_order_id}&task_type=RAW_TO_PRODUCTION&limit=20"
    )
    if not confirmed_warehouse_tasks:
        raise AssertionError("Expected RAW_TO_PRODUCTION warehouse task for confirmed raw supply task.")
    if not any(task.get("status") == "DONE" for task in confirmed_warehouse_tasks):
        raise AssertionError("Expected confirmed RAW_TO_PRODUCTION warehouse task to be DONE.")
    sync = client.get(f"/api/warehouse-tasks/{confirm_warehouse_task['task_id']}/sync")
    if sync.get("sync_status") != "SYNCED":
        raise AssertionError(f"Expected RAW_TO_PRODUCTION sync SYNCED, got {sync}")

    partial_bom_id, partial_target = create_bom(client, suffix + "P")
    partial_order_id, partial_tasks = create_and_release_order(
        client,
        1000,
        partial_bom_id,
        partial_target,
        suffix,
        planned_qty=2,
    )
    partial_task = next(task for task in partial_tasks if task.get("task_status") == "PLANNED")
    partial_warehouse_task = find_warehouse_task_for_raw_task(client, partial_order_id, partial_task["task_id"])
    complete_warehouse_task(client, partial_warehouse_task, fact_qty=1)
    partially_confirmed_task = client.get(f"/api/mes/raw-transfer-tasks/{partial_task['task_id']}")
    if partially_confirmed_task.get("task_status") != "IN_PROGRESS":
        raise AssertionError(f"Expected partial raw task IN_PROGRESS, got {partially_confirmed_task}")
    residual_task = next(
        task
        for task in client.get(
            f"/api/warehouse-tasks?production_order_id={partial_order_id}&task_type=RAW_TO_PRODUCTION&limit=20"
        )
        if task.get("status") == "PLANNED"
        and int(task.get("parent_task_id") or 0) == int(partial_warehouse_task["task_id"])
    )
    complete_warehouse_task(client, residual_task)
    completed_partial_task = client.get(f"/api/mes/raw-transfer-tasks/{partial_task['task_id']}")
    if completed_partial_task.get("task_status") != "DONE":
        raise AssertionError(f"Expected partial raw task DONE after residual, got {completed_partial_task}")
    partial_sync_rows = client.get(
        f"/api/warehouse-tasks/domain-sync?task_source=MES_RAW_SUPPLY&source_doc_id={partial_order_id}&limit=20"
    )
    if len([row for row in partial_sync_rows if row.get("sync_status") == "SYNCED"]) < 2:
        raise AssertionError(f"Expected both partial sync rows SYNCED, got {partial_sync_rows}")

    for task_id in created_tasks:
        client.post(
            f"/api/mes/raw-transfer-tasks/{task_id}/cancel",
            {"reason": "raw supply smoke cleanup", "cancelled_by": "raw-supply-smoke"},
        )

    diagnostics = {
        "active_hard_raw_supply_smoke": client.get(
            "/api/stock-reservations"
            "?reservation_domain=MES_RAW&reservation_kind=HARD&only_active=1"
            "&limit=1000"
        ),
        "cancelled_tasks": client.get(
            "/api/mes/raw-transfer-tasks?status=CANCELLED&limit=1000"
        ),
    }
    active_smoke_reservations = [
        row
        for row in diagnostics["active_hard_raw_supply_smoke"]
        if row.get("created_by") == "raw-supply-smoke"
    ]
    if active_smoke_reservations:
        raise AssertionError(f"Smoke left active hard reservations: {active_smoke_reservations[:5]}")

    elapsed = time.perf_counter() - started
    print(json.dumps({
        "status": "ok",
        "bom_id": bom_id,
        "orders_released": len(created_orders),
        "tasks_cancelled": len(created_tasks),
        "confirm_order_id": confirm_order_id,
        "confirm_task_id": confirm_task["task_id"],
        "confirm_warehouse_task_id": confirm_warehouse_task["task_id"],
        "partial_order_id": partial_order_id,
        "partial_task_id": partial_task["task_id"],
        "confirmed_warehouse_tasks": len(confirmed_warehouse_tasks),
        "elapsed_sec": round(elapsed, 3),
        "ops_per_sec": round((args.orders * 3 + 10) / elapsed, 2),
    }, ensure_ascii=False, indent=2))
    return 0


def create_bom(client: "Client", suffix: str) -> tuple[int, str]:
    target = f"FG-RAW-SUPPLY-{suffix}"
    bom = client.post("/api/bom", {
        "bom_code": f"RAW-SUPPLY-BOM-{suffix}",
        "bom_name": "Raw supply smoke BOM",
        "target_articul": target,
        "base_qty": 1,
        "base_unit_code": "KG",
        "is_primary": 1,
        "valid_from": date.today().isoformat(),
        "created_by": "raw-supply-smoke",
    })
    bom_id = int(bom["id"])
    client.post(f"/api/bom/{bom_id}/lines", {
        "line_no": 10,
        "component_type": "RAW",
        "component_articul": RAW_ARTICUL,
        "component_name": "Beef frozen block",
        "qty_per_base": 1,
        "unit_code": "KG",
        "created_by": "raw-supply-smoke",
    })
    client.post(f"/api/bom/{bom_id}/approve", {"user_name": "raw-supply-smoke"})
    return bom_id, target


def create_and_release_order(
    client: "Client",
    index: int,
    bom_id: int,
    target: str,
    suffix: str,
    planned_qty: float = 1,
) -> tuple[int, list[dict]]:
    order = client.post("/api/mes/production-orders", {
        "order_no": f"RAW-SUPPLY-{suffix}-{index:03d}",
        "bom_id": bom_id,
        "target_articul": target,
        "planned_qty": planned_qty,
        "unit_code": "KG",
        "ware_id": TO_WARE_ID,
        "production_line": "LINE-SMOKE",
        "idempotency_key": f"raw-supply-{suffix}-{index:03d}",
        "created_by": "raw-supply-smoke",
    })
    order_id = int(order["id"])
    result = client.post(f"/api/mes/production-orders/{order_id}/release-to-production", {
        "to_ware_id": TO_WARE_ID,
        "to_cell": TO_CELL,
        "allow_partial": 0,
        "created_by": "raw-supply-smoke",
    })
    if result.get("shortage_count"):
        raise AssertionError(f"Unexpected shortage for order {order_id}: {result}")
    tasks = client.get(f"/api/mes/raw-transfer-tasks?production_order_id={order_id}&limit=20")
    if not any(task.get("task_status") == "PLANNED" for task in tasks):
        raise AssertionError(f"Expected planned raw transfer task for order {order_id}")
    return order_id, tasks


def find_warehouse_task_for_raw_task(client: "Client", order_id: int, raw_task_id: int) -> dict:
    tasks = client.get(f"/api/warehouse-tasks?production_order_id={order_id}&task_type=RAW_TO_PRODUCTION&limit=20")
    return next(task for task in tasks if int(task.get("source_task_id") or 0) == int(raw_task_id))


def complete_warehouse_task(client: "Client", warehouse_task: dict, fact_qty: float | None = None) -> None:
    payload = {
        "assigned_to": "raw-supply-smoke",
        "scanned_pallet": warehouse_task.get("uid_pallet") or warehouse_task.get("sscc"),
        "scanned_from_cell": warehouse_task.get("from_cell"),
        "scanned_to_cell": warehouse_task.get("to_cell"),
    }
    if fact_qty is not None:
        payload["fact_qty"] = fact_qty
    client.post(f"/api/warehouse-tasks/{warehouse_task['task_id']}/assign", payload)
    client.post(f"/api/warehouse-tasks/{warehouse_task['task_id']}/start", payload)
    client.post(f"/api/warehouse-tasks/{warehouse_task['task_id']}/complete", payload)


class Client:
    def __init__(self, base_url: str, user: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        token = base64.b64encode(f"{user}:{password}".encode("ascii")).decode("ascii")
        self.auth_header = f"Basic {token}"

    def request(self, method: str, path: str, payload=None, auth: bool = True):
        data = None
        headers = {"Accept": "application/json"}
        if auth:
            headers["Authorization"] = self.auth_header
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{method} {path} failed: HTTP {exc.code}: {body}") from exc
        return json.loads(body) if body else {}

    def get(self, path: str, auth: bool = True):
        return self.request("GET", path, auth=auth)

    def post(self, path: str, payload):
        return self.request("POST", path, payload=payload)


if __name__ == "__main__":
    raise SystemExit(main())
