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


WARE_ID = -41221
CREATED_BY = "SMOKE_020_HTTP"


def main() -> None:
    gateway = OracleGateway()
    cleanup(gateway)
    try:
        gateway.execute(
            "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
            {"ware_id": WARE_ID, "name": "SMOKE 020 HTTP MAP DB SWITCH", "prefix": "H20"},
        )
        draft = post_json(
            "/api/admin/warehouse-map-drafts",
            {
                "draft_name": "Smoke 020 HTTP draft",
                "grid": {"aisle_count": 4, "slots_per_aisle": 6, "levels": 2},
                "created_by": CREATED_BY,
            },
        )
        draft_id = draft["draft_id"]
        post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/bulk-role",
            {
                "role": "PICK_FACE",
                "selection": {"aisle_from": 1, "aisle_to": 2, "slot_from": 1, "slot_to": 4, "level_from": 1, "level_to": 1},
                "updated_by": CREATED_BY,
            },
        )
        route = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/route/build",
            {
                "selection": {"aisle_from": 1, "aisle_to": 2, "slot_from": 1, "slot_to": 4, "level_from": 1, "level_to": 1},
                "route_code": "SMOKE-020-HTTP-PICK",
                "route_name": "Smoke 020 HTTP route",
                "route_pattern": "Z",
                "updated_by": CREATED_BY,
            },
        )
        saved = post_json(
            f"/api/admin/warehouse-map-drafts/{draft_id}/save-to-db",
            {
                "ware_id": WARE_ID,
                "canvas_code": "SMOKE-020-HTTP-CANVAS",
                "canvas_name": "Smoke 020 HTTP canvas",
                "camera_code": "SMOKE-020-HTTP-MAIN",
                "camera_name": "Smoke 020 HTTP main camera",
                "updated_by": CREATED_BY,
            },
        )
        loaded = post_json(
            "/api/admin/warehouse-map-drafts/load-from-db",
            {"canvas_id": saved["canvas_id"], "draft_name": "Smoke 020 HTTP loaded", "created_by": CREATED_BY},
        )
        validation = post_json(f"/api/admin/warehouse-map-drafts/{loaded['draft_id']}/validate", {})
        direct = direct_counts(gateway, int(saved["canvas_id"]))

        assert saved["status"] == "SAVED_TO_DB", saved
        assert route["route_row_count"] == saved["route_row_count"] == 8
        assert len(loaded["route_rows"]) == 8
        assert validation["valid"], validation
        assert direct["canvas_payload_count"] == 1, direct
        assert direct["camera_count"] == 1, direct

        print(json.dumps({
            "status": "ok",
            "draft_id": draft_id,
            "loaded_draft_id": loaded["draft_id"],
            "canvas_id": saved["canvas_id"],
            "camera_id": saved["camera_id"],
            "route_row_count": saved["route_row_count"],
            "loaded_valid": validation["valid"],
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


def direct_counts(gateway: OracleGateway, canvas_id: int) -> dict[str, int]:
    rows = gateway.fetch_all(
        """
        select 'canvas_payload_count' key, count(*) value
          from RRL_WAREHOUSE_MAP_CANVAS
         where CANVAS_ID = :canvas_id
           and RENDERER_STATE_JSON is not null
           and dbms_lob.instr(RENDERER_STATE_JSON, 'warehouse_map_draft_payload_version') > 0
        union all
        select 'camera_count', count(*)
          from RRL_WAREHOUSE_MAP_CAMERA
         where CANVAS_ID = :canvas_id
           and ACTIVE = 1
        """,
        {"canvas_id": canvas_id},
    )
    return {str(row["key"]): int(row["value"] or 0) for row in rows}


def cleanup(gateway: OracleGateway) -> None:
    statements: list[tuple[str, dict[str, Any]]] = [
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
