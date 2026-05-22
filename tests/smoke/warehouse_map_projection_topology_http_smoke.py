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


WARE_ID = -41223
CREATED_BY = "SMOKE_021_HTTP"


def main() -> None:
    gateway = OracleGateway()
    cleanup(gateway)
    try:
        gateway.execute(
            "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
            {"ware_id": WARE_ID, "name": "SMOKE 021 HTTP MAP PROJECTION", "prefix": "H21"},
        )
        draft = post_json(
            "/api/admin/warehouse-map-drafts",
            {
                "draft_name": "Smoke 021 HTTP projection draft",
                "grid": {"aisle_count": 4, "slots_per_aisle": 6, "levels": 2},
                "created_by": CREATED_BY,
            },
        )
        draft_id = draft["draft_id"]
        post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/small-pick-faces/generate",
            {
                "physical_cell": {"aisle": 1, "slot": 1, "level": 1},
                "fraction_cell_count": 2,
                "sub_level_count": 2,
                "sub_column_count": 1,
                "code_mask": "{physical_cell}-P{sub_level}",
                "updated_by": CREATED_BY,
            },
        )
        post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/storage-slots/generate",
            {
                "physical_cell": {"aisle": 2, "slot": 1, "level": 1},
                "fraction_cell_count": 2,
                "sub_level_count": 1,
                "sub_column_count": 2,
                "code_mask": "{physical_cell}-S{sub_column}",
                "updated_by": CREATED_BY,
            },
        )
        post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/bulk-role",
            {
                "role": "AISLE",
                "selection": {"aisle_from": 3, "aisle_to": 3, "slot_from": 1, "slot_to": 1, "level_from": 1, "level_to": 1},
                "updated_by": CREATED_BY,
            },
        )
        saved = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/save-to-db",
            {
                "ware_id": WARE_ID,
                "canvas_code": "SMOKE-021-HTTP-CANVAS",
                "canvas_name": "Smoke 021 HTTP canvas",
                "camera_code": "SMOKE-021-HTTP-MAIN",
                "camera_name": "Smoke 021 HTTP main camera",
                "updated_by": CREATED_BY,
            },
        )
        projection = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/projection/save-to-topology",
            {
                "ware_id": WARE_ID,
                "topology_code": "SMOKE-021-HTTP-TOPO",
                "topology_name": "Smoke 021 HTTP topology",
                "updated_by": CREATED_BY,
            },
        )
        direct = direct_counts(gateway, int(projection["topology_id"]), int(saved["canvas_id"]))

        assert projection["status"] == "SAVED_TO_TOPOLOGY", projection
        assert projection["topology_cell_count"] == 3, projection
        assert projection["pick_face_slot_count"] == 2, projection
        assert projection["storage_slot_count"] == 2, projection
        assert direct["cell_count"] == 3, direct
        assert direct["pick_slot_count"] == 2, direct
        assert direct["storage_slot_count"] == 2, direct
        assert direct["storage_slots_in_route"] == 0, direct

        print(json.dumps({
            "status": "ok",
            "draft_id": draft_id,
            "canvas_id": saved["canvas_id"],
            "topology_id": projection["topology_id"],
            "projection": projection,
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


def direct_counts(gateway: OracleGateway, topology_id: int, canvas_id: int) -> dict[str, int]:
    rows = gateway.fetch_all(
        """
        select 'cell_count' key, count(*) value
          from RRL_TOPOLOGY_CELL
         where TOPOLOGY_ID = :topology_id
           and ACTIVE = 1
        union all
        select 'pick_slot_count', count(*)
          from RRL_TOPOLOGY_CELL_SLOT
         where TOPOLOGY_ID = :topology_id
           and SLOT_KIND = 'PICK_FACE_SLOT'
           and ACTIVE = 1
        union all
        select 'storage_slot_count', count(*)
          from RRL_TOPOLOGY_CELL_SLOT
         where TOPOLOGY_ID = :topology_id
           and SLOT_KIND = 'STORAGE_SLOT'
           and ACTIVE = 1
        union all
        select 'canvas_topology_link_count', count(*)
          from RRL_WAREHOUSE_MAP_CANVAS
         where CANVAS_ID = :canvas_id
           and TOPOLOGY_ID = :topology_id
        union all
        select 'storage_slots_in_route', count(*)
          from RRL_PICK_ROUTE_CELL rc
          join RRL_TOPOLOGY_CELL_SLOT s
            on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
         where s.TOPOLOGY_ID = :topology_id
           and s.SLOT_KIND = 'STORAGE_SLOT'
           and rc.ACTIVE = 1
        """,
        {"topology_id": topology_id, "canvas_id": canvas_id},
    )
    return {str(row["key"]): int(row["value"] or 0) for row in rows}


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
