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


WARE_ID = -41227
CREATED_BY = "SMOKE_023_HTTP"


def main() -> None:
    gateway = OracleGateway()
    cleanup(gateway)
    try:
        gateway.execute(
            "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
            {"ware_id": WARE_ID, "name": "SMOKE 023 HTTP MAP PUBLISH", "prefix": "H23"},
        )
        draft = post_json(
            "/api/admin/warehouse-map-drafts",
            {
                "draft_name": "Smoke 023 HTTP publish draft",
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
                "route_code": "SMOKE-023-HTTP-PICK",
                "route_name": "Smoke 023 HTTP route",
                "route_pattern": "LINEAR",
                "updated_by": CREATED_BY,
            },
        )
        saved = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/save-to-db",
            {
                "ware_id": WARE_ID,
                "canvas_code": "SMOKE-023-HTTP-CANVAS",
                "canvas_name": "Smoke 023 HTTP canvas",
                "camera_code": "SMOKE-023-HTTP-MAIN",
                "camera_name": "Smoke 023 HTTP main camera",
                "updated_by": CREATED_BY,
            },
        )
        projection = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/projection/save-to-topology",
            {
                "ware_id": WARE_ID,
                "topology_code": "SMOKE-023-HTTP-TOPO",
                "topology_name": "Smoke 023 HTTP topology",
                "updated_by": CREATED_BY,
            },
        )
        route_save = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/route/save-to-db",
            {
                "ware_id": WARE_ID,
                "topology_id": projection["topology_id"],
                "route_code": "SMOKE-023-HTTP-PICK",
                "route_name": "Smoke 023 HTTP route",
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
        direct = direct_status(gateway, int(saved["canvas_id"]), int(projection["topology_id"]), int(route_save["pick_route_id"]))

        assert route["route_row_count"] == 3, route
        assert published["oracle_validation"]["valid"], published
        assert direct["canvas_status"] == "PUBLISHED", direct
        assert direct["topology_status"] == "PUBLISHED", direct
        assert direct["route_status"] == "PUBLISHED", direct
        assert direct["route_row_count"] == 3, direct
        assert direct["storage_slot_rows"] == 0, direct

        print(json.dumps({
            "status": "ok",
            "draft_id": draft_id,
            "canvas_id": saved["canvas_id"],
            "topology_id": projection["topology_id"],
            "pick_route_id": route_save["pick_route_id"],
            "published": published,
            "direct": direct,
        }, ensure_ascii=False, indent=2, default=str))
    finally:
        cleanup(gateway)


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


def direct_status(gateway: OracleGateway, canvas_id: int, topology_id: int, pick_route_id: int) -> dict[str, Any]:
    rows = gateway.fetch_all(
        """
        select c.STATUS CANVAS_STATUS,
               t.STATUS TOPOLOGY_STATUS,
               r.STATUS ROUTE_STATUS,
               (select count(*)
                  from RRL_PICK_ROUTE_CELL
                 where PICK_ROUTE_ID = :pick_route_id
                   and ACTIVE = 1) ROUTE_ROW_COUNT,
               (select count(*)
                  from RRL_PICK_ROUTE_CELL rc
                  join RRL_TOPOLOGY_CELL_SLOT s
                    on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
                 where rc.PICK_ROUTE_ID = :pick_route_id
                   and s.SLOT_KIND = 'STORAGE_SLOT'
                   and rc.ACTIVE = 1) STORAGE_SLOT_ROWS
          from RRL_WAREHOUSE_MAP_CANVAS c
          join RRL_WAREHOUSE_TOPOLOGY t
            on t.TOPOLOGY_ID = :topology_id
          join RRL_PICK_ROUTE r
            on r.PICK_ROUTE_ID = :pick_route_id
         where c.CANVAS_ID = :canvas_id
        """,
        {"canvas_id": canvas_id, "topology_id": topology_id, "pick_route_id": pick_route_id},
    )
    if not rows:
        raise AssertionError("Published Oracle rows were not found.")
    return rows[0]


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
