import argparse
import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date


def main() -> int:
    parser = argparse.ArgumentParser(description="WMS/MES HTTP workflow smoke test.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8088")
    parser.add_argument("--user", default="admin")
    parser.add_argument("--password", default="admin123")
    args = parser.parse_args()

    client = Client(args.base_url, args.user, args.password)
    suffix = time.strftime("%Y%m%d%H%M%S")
    target_articul = f"FG-HTTP-PETFOOD-{suffix}"
    raw_articul = "RM-MEAT-BEEF-FROZ-01"
    bom_code = f"HTTP-MES-BOM-{suffix}"
    order_no = f"HTTP-MES-ORDER-{suffix}"
    lot_no = f"HTTP-MES-LOT-{suffix}"
    raw_pallet = f"HTTP-MES-RAW-{suffix}"
    fg_pallet = f"HTTP-MES-FG-{suffix}"
    fg_target_cell = "FG-A01-01"

    client.get("/health", auth=False)

    bom = client.post("/api/bom", {
        "bom_code": bom_code,
        "bom_name": "HTTP MES smoke BOM",
        "target_articul": target_articul,
        "base_qty": 100,
        "base_unit_code": "KG",
        "is_primary": 1,
        "valid_from": date.today().isoformat(),
        "created_by": "http-smoke",
    })
    bom_id = bom["id"]

    client.post(f"/api/bom/{bom_id}/lines", {
        "line_no": 10,
        "component_type": "RAW",
        "component_articul": raw_articul,
        "component_name": "Beef frozen block",
        "qty_per_base": 50,
        "unit_code": "KG",
        "created_by": "http-smoke",
    })
    client.post(f"/api/bom/{bom_id}/approve", {"user_name": "http-smoke"})
    default_bom = client.get(f"/api/bom/default?target_articul={target_articul}&planned_date={date.today().isoformat()}")
    if default_bom["bom_id"] != bom_id:
        raise AssertionError(f"Expected default BOM {bom_id}, got {default_bom['bom_id']}")

    order = client.post("/api/mes/production-orders", {
        "order_no": order_no,
        "bom_id": bom_id,
        "target_articul": target_articul,
        "planned_qty": 100,
        "unit_code": "KG",
        "ware_id": 9102,
        "production_line": "LINE-HTTP",
        "idempotency_key": f"{order_no}:create",
        "created_by": "http-smoke",
    })
    order_id = order["id"]

    client.post(f"/api/mes/production-orders/{order_id}/issue-raw", {
        "uid_pallet": raw_pallet,
        "raw_articul": raw_articul,
        "quantity": 50,
        "unit_code": "KG",
        "source_location": "RM-A01-01",
        "production_location": "MES_PROD",
        "created_by": "http-smoke",
    })

    client.post(f"/api/mes/production-orders/{order_id}/complete", {
        "prod_batch_no": lot_no,
        "fact_qty": 100,
        "unit_code": "KG",
        "pallets": [{
            "uid_pallet": fg_pallet,
            "pallet_no": 1,
            "quantity": 100,
            "pack_count": 10,
            "sscc": ("0000000000" + suffix)[-18:],
            "target_ware_id": 9104,
            "target_cell": fg_target_cell,
        }],
        "idempotency_key": f"{order_no}:complete",
        "created_by": "http-smoke",
    })

    client.post(f"/api/mes/production-orders/{order_id}/apply-wms", {"applied_by": "http-smoke"})
    detail = client.get(f"/api/mes/production-orders/{order_id}")
    genealogy = client.get(f"/api/mes/production-orders/{order_id}/genealogy")
    prod_batch_id = genealogy.get("order", {}).get("prod_batch_id")

    movements = detail.get("movements", [])
    applied = [m for m in movements if m.get("status") == "APPLIED_TO_WMS"]
    if len(applied) < 3:
        raise AssertionError(f"Expected at least 3 applied movements, got {len(applied)}")
    if not genealogy.get("raw_usage"):
        raise AssertionError("Expected raw usage in genealogy.")
    if not genealogy.get("pallets"):
        raise AssertionError("Expected finished-goods pallets in genealogy.")
    if not prod_batch_id:
        raise AssertionError("Expected production batch id in genealogy.")

    fg_batches = client.get(f"/api/finished-goods/batches?batch_no={urllib.parse.quote(lot_no)}&limit=5")
    fg_remains = client.get(f"/api/finished-goods/remains?prod_batch_no={urllib.parse.quote(lot_no)}&limit=5")
    if not fg_batches:
        raise AssertionError("Expected finished-goods batch to be visible in finished-goods admin API.")
    if not fg_remains:
        raise AssertionError("Expected finished-goods pallet remain to be visible in finished-goods admin API.")

    warehouse_tasks = client.get(f"/api/warehouse-tasks?production_order_id={order_id}&limit=20")
    fg_storage_tasks = [task for task in warehouse_tasks if task.get("task_type") == "FG_TO_STORAGE"]
    if not fg_storage_tasks:
        raise AssertionError("Expected FG_TO_STORAGE warehouse task for released finished-goods pallet.")
    fg_storage_task = fg_storage_tasks[0]
    if fg_storage_task.get("to_cell") != fg_target_cell:
        raise AssertionError(f"Expected FG target cell {fg_target_cell}, got {fg_storage_task.get('to_cell')}")
    complete_warehouse_task(client, fg_storage_task, "http-smoke")
    fg_sync = client.get(f"/api/warehouse-tasks/{fg_storage_task['task_id']}/sync")
    if fg_sync.get("sync_status") != "SYNCED":
        raise AssertionError(f"Expected FG_TO_STORAGE sync SYNCED, got {fg_sync}")

    raw_trace = client.get(f"/api/trace/entities/RAW_MATERIAL_PALLET/{urllib.parse.quote(raw_pallet)}/forward")
    order_trace = client.get(f"/api/trace/entities/PRODUCTION_ORDER/{order_id}/forward")
    lot_trace = client.get(f"/api/trace/entities/FINISHED_GOODS_LOT/{prod_batch_id}/forward")
    pallet_trace = client.get(f"/api/trace/entities/PALLET/{urllib.parse.quote(fg_pallet)}/forward")
    if not raw_trace:
        raise AssertionError("Expected raw pallet -> production order trace edge.")
    if not order_trace:
        raise AssertionError("Expected production order -> finished goods lot trace edge.")
    if not lot_trace:
        raise AssertionError("Expected finished goods lot -> pallet trace edge.")
    if not pallet_trace:
        raise AssertionError("Expected pallet -> SSCC trace edge.")

    outbox = client.get(
        f"/api/admin/event-outbox?aggregate_type=PRODUCTION_ORDER&aggregate_id={order_id}"
        "&event_type=PRODUCTION_COMPLETED&limit=5"
    )
    if not outbox:
        raise AssertionError("Expected PRODUCTION_COMPLETED event in durable outbox.")

    api_audit = client.get("/api/admin/api-calls?path_like=/api/mes/production-orders&limit=20")
    if not api_audit:
        raise AssertionError("Expected MES API calls in API audit log.")
    slow_sql = client.get("/api/admin/slow-sql?path_like=/api/mes&min_elapsed_ms=0&limit=20")

    print(json.dumps({
        "status": "ok",
        "bom_id": bom_id,
        "production_order_id": order_id,
        "order_no": order_no,
        "lot_no": lot_no,
        "movements": len(movements),
        "applied_movements": len(applied),
        "raw_usage": len(genealogy.get("raw_usage", [])),
        "pallets": len(genealogy.get("pallets", [])),
        "finished_goods_batches": len(fg_batches),
        "finished_goods_remains": len(fg_remains),
        "warehouse_tasks": len(warehouse_tasks),
        "fg_storage_tasks": len(fg_storage_tasks),
        "trace_edges": {
            "raw_to_order": len(raw_trace),
            "order_to_lot": len(order_trace),
            "lot_to_pallet": len(lot_trace),
            "pallet_to_sscc": len(pallet_trace),
        },
        "outbox_events": len(outbox),
        "api_audit_calls": len(api_audit),
        "slow_sql_rows": len(slow_sql),
    }, ensure_ascii=False, indent=2))
    return 0


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
        req = urllib.request.Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{method} {path} failed: HTTP {exc.code}: {body}") from exc
        return json.loads(body) if body else {}

    def get(self, path: str, auth: bool = True):
        return self.request("GET", path, auth=auth)

    def post(self, path: str, payload):
        return self.request("POST", path, payload=payload)


def complete_warehouse_task(client: Client, warehouse_task: dict, user_name: str) -> None:
    payload = {
        "assigned_to": user_name,
        "scanned_pallet": warehouse_task.get("uid_pallet") or warehouse_task.get("sscc"),
        "scanned_from_cell": warehouse_task.get("from_cell"),
        "scanned_to_cell": warehouse_task.get("to_cell"),
    }
    client.post(f"/api/warehouse-tasks/{warehouse_task['task_id']}/assign", payload)
    client.post(f"/api/warehouse-tasks/{warehouse_task['task_id']}/start", payload)
    client.post(f"/api/warehouse-tasks/{warehouse_task['task_id']}/complete", payload)


if __name__ == "__main__":
    raise SystemExit(main())
