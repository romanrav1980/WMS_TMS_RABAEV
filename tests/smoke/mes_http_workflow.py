import argparse
import base64
import json
import time
import urllib.error
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
    target_articul = "FG-HTTP-PETFOOD"
    raw_articul = "RM-MEAT-BEEF-FROZ-01"
    bom_code = f"HTTP-MES-BOM-{suffix}"
    order_no = f"HTTP-MES-ORDER-{suffix}"
    lot_no = f"HTTP-MES-LOT-{suffix}"
    raw_pallet = f"HTTP-MES-RAW-{suffix}"
    fg_pallet = f"HTTP-MES-FG-{suffix}"

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
        }],
        "idempotency_key": f"{order_no}:complete",
        "created_by": "http-smoke",
    })

    client.post(f"/api/mes/production-orders/{order_id}/apply-wms", {"applied_by": "http-smoke"})
    detail = client.get(f"/api/mes/production-orders/{order_id}")
    genealogy = client.get(f"/api/mes/production-orders/{order_id}/genealogy")

    movements = detail.get("movements", [])
    applied = [m for m in movements if m.get("status") == "APPLIED_TO_WMS"]
    if len(applied) < 3:
        raise AssertionError(f"Expected at least 3 applied movements, got {len(applied)}")
    if not genealogy.get("raw_usage"):
        raise AssertionError("Expected raw usage in genealogy.")
    if not genealogy.get("pallets"):
        raise AssertionError("Expected finished-goods pallets in genealogy.")

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


if __name__ == "__main__":
    raise SystemExit(main())
