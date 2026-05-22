from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "api" / "wms_api_server"))

from app.oracle_gateway import OracleGateway  # noqa: E402


WARE_ID = -41228
CREATED_BY = "SMOKE_025_HTTP"


def main() -> None:
    gateway = OracleGateway()
    cleanup(gateway)
    try:
        gateway.execute(
            "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
            {"ware_id": WARE_ID, "name": "SMOKE 025 HTTP PUBLISHED RELOAD", "prefix": "H25"},
        )
        draft = post_json(
            "/api/admin/warehouse-map-drafts",
            {
                "draft_name": "Smoke 025 HTTP published reload draft",
                "grid": {"aisle_count": 4, "slots_per_aisle": 6, "levels": 1},
                "created_by": CREATED_BY,
            },
        )
        draft_id = draft["draft_id"]
        post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/bulk-role",
            {
                "role": "PICK_FACE",
                "selection": {"aisle_from": 1, "aisle_to": 2, "slot_from": 1, "slot_to": 1, "level_from": 1, "level_to": 1},
                "updated_by": CREATED_BY,
            },
        )
        post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/generate",
            {
                "physical_cell": {"aisle": 3, "slot": 1, "level": 1},
                "fraction_cell_count": 2,
                "sub_level_count": 2,
                "sub_column_count": 1,
                "code_mask": "{physical_cell}-P{sub_level}",
                "updated_by": CREATED_BY,
            },
        )
        route = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/route/build",
            {
                "selection": {"aisle_from": 1, "aisle_to": 3, "slot_from": 1, "slot_to": 1, "level_from": 1, "level_to": 1},
                "route_code": "SMOKE-025-HTTP-PICK",
                "route_name": "Smoke 025 HTTP route",
                "route_pattern": "LINEAR",
                "updated_by": CREATED_BY,
            },
        )
        saved = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/save-to-db",
            {
                "ware_id": WARE_ID,
                "canvas_code": "SMOKE-025-HTTP-CANVAS",
                "canvas_name": "Smoke 025 HTTP canvas",
                "camera_code": "SMOKE-025-HTTP-MAIN",
                "camera_name": "Smoke 025 HTTP main camera",
                "updated_by": CREATED_BY,
            },
        )
        projection = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/projection/save-to-topology",
            {
                "ware_id": WARE_ID,
                "topology_code": "SMOKE-025-HTTP-TOPO",
                "topology_name": "Smoke 025 HTTP topology",
                "updated_by": CREATED_BY,
            },
        )
        route_save = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/route/save-to-db",
            {
                "ware_id": WARE_ID,
                "topology_id": projection["topology_id"],
                "route_code": "SMOKE-025-HTTP-PICK",
                "route_name": "Smoke 025 HTTP route",
                "updated_by": CREATED_BY,
            },
        )
        published = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/publish-oracle",
            {
                "canvas_id": saved["canvas_id"],
                "topology_id": projection["topology_id"],
                "pick_route_id": route_save["pick_route_id"],
                "published_by": CREATED_BY,
            },
        )
        state = get_json(f"/api/admin/warehouse-map/warehouses/{WARE_ID}/state")
        canvases = get_json(f"/api/admin/warehouse-map/warehouses/{WARE_ID}/canvases")

        routes = state.get("routes") or []
        active_route = routes[0] if routes else {}
        route_rows = active_route.get("route_rows") or []

        assert route["route_row_count"] == 3, route
        assert published["status"] == "PUBLISHED", published
        assert state["canvas"]["status"] == "PUBLISHED", state
        assert state["topology"]["status"] == "PUBLISHED", state
        assert active_route["status"] == "PUBLISHED", state
        assert active_route["route_row_count"] == 3, state
        assert len(route_rows) == 3, state
        assert state["counters"]["route_rows"] == 3, state
        assert state["counters"]["route_rows_excluded_storage_slots"] == 0, state
        assert canvases[0]["status"] == "PUBLISHED", canvases

        print(json.dumps({
            "status": "ok",
            "draft_id": draft_id,
            "canvas_id": saved["canvas_id"],
            "topology_id": projection["topology_id"],
            "pick_route_id": route_save["pick_route_id"],
            "published": published["status"],
            "reload": {
                "canvas_status": state["canvas"]["status"],
                "topology_status": state["topology"]["status"],
                "route_status": active_route["status"],
                "route_row_count": active_route["route_row_count"],
                "state_route_rows": state["counters"]["route_rows"],
                "excluded_storage_rows": state["counters"]["route_rows_excluded_storage_slots"],
            },
        }, ensure_ascii=False, indent=2, default=str))
    finally:
        cleanup(gateway)


def get_json(path: str) -> Any:
    request = urllib.request.Request(
        f"{base_url()}{path}",
        method="GET",
        headers={
            "Authorization": f"Basic {auth_token()}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(path: str, payload: dict[str, Any]) -> Any:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url()}{path}",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {auth_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def base_url() -> str:
    return os.getenv("WAREHOUSE_MAP_API_BASE_URL", "http://127.0.0.1:8088").rstrip("/")


def auth_token() -> str:
    username = os.getenv("WAREHOUSE_MAP_API_USER", "admin")
    password = os.getenv("WAREHOUSE_MAP_API_PASSWORD", "admin123")
    return base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")


def cleanup(gateway: OracleGateway) -> None:
    statements: list[tuple[str, dict[str, Any]]] = [
        ("delete from RRL_PICK_ROUTE_CELL where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_PICK_ROUTE where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("update RRL_WAREHOUSE_MAP_CANVAS set TOPOLOGY_ID = null where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_TOPOLOGY_CELL where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CAMERA_LINK where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_PASSAGE where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_OBJECT where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CAMERA where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WARES where ID = :ware_id", {"ware_id": WARE_ID}),
    ]
    for sql, params in statements:
        gateway.execute(sql, params)


if __name__ == "__main__":
    main()
