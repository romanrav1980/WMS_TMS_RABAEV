from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "api" / "wms_api_server"))

from app.oracle_gateway import OracleGateway  # noqa: E402


WARE_ID = -41212
CREATED_BY = "SMOKE_012"


def main() -> None:
    gateway = OracleGateway()
    cleanup(gateway)
    try:
        gateway.execute(
            "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
            {"ware_id": WARE_ID, "name": "SMOKE 012 MAP CAMERA", "prefix": "S12"},
        )
        canvas_state = post_json(
            f"/api/admin/warehouse-map/warehouses/{WARE_ID}/canvases",
            {
                "canvas_code": "SMOKE-012-CANVAS",
                "canvas_name": "Smoke 012 canvas",
                "levels": 6,
                "created_by": CREATED_BY,
            },
        )
        canvas_id = int(canvas_state["canvas"]["canvas_id"])
        camera_result = post_json(
            f"/api/admin/warehouse-map/canvases/{canvas_id}/cameras",
            {
                "camera_code": "CAM-01",
                "camera_name": "Smoke camera 01",
                "camera_kind": "DRY",
                "origin_x_m": 0,
                "origin_y_m": 0,
                "origin_z_m": 0,
                "width_m": 42,
                "depth_m": 90,
                "height_m": 12,
                "levels": 6,
                "default_passage_width_m": 3,
                "default_aisle_spacing_m": 3.6,
                "boundary_json": {"shape": "rect"},
                "created_by": CREATED_BY,
            },
        )
        camera_id = int(camera_result["camera"]["camera_id"])
        duplicate_status = post_expect_error(
            f"/api/admin/warehouse-map/canvases/{canvas_id}/cameras",
            {
                "camera_code": "CAM-01",
                "camera_name": "Duplicate camera",
                "width_m": 42,
                "depth_m": 90,
                "height_m": 12,
                "created_by": CREATED_BY,
            },
        )
        clone_result = post_json(
            f"/api/admin/warehouse-map/cameras/{camera_id}/clone",
            {
                "camera_code": "CAM-02",
                "camera_name": "Smoke camera 02",
                "origin_x_m": 45,
                "created_by": CREATED_BY,
            },
        )
        clone_id = int(clone_result["camera"]["camera_id"])
        archive_clone = post_json(
            f"/api/admin/warehouse-map/cameras/{clone_id}/archive",
            {"reason": "smoke success path", "updated_by": CREATED_BY},
        )
        gateway.execute(
            """
            insert into RRL_WAREHOUSE_MAP_OBJECT (
              MAP_OBJECT_ID, CANVAS_ID, CAMERA_ID, OBJECT_CODE, OBJECT_KIND, OBJECT_NAME,
              X_M, Y_M, Z_M, WIDTH_M, DEPTH_M, HEIGHT_M, CREATED_BY, UPDATED_BY
            ) values (
              RRL_WH_MAP_OBJECT_SQ.nextval, :canvas_id, :camera_id, 'SMOKE-012-WALL', 'WALL', 'Smoke wall',
              1, 1, 0, 1, 1, 3, :created_by, :created_by
            )
            """,
            {"canvas_id": canvas_id, "camera_id": camera_id, "created_by": CREATED_BY},
        )
        blocked_status = post_expect_error(
            f"/api/admin/warehouse-map/cameras/{camera_id}/archive",
            {"reason": "must be blocked", "updated_by": CREATED_BY},
        )
        state = get_json(f"/api/admin/warehouse-map/warehouses/{WARE_ID}/state")
        direct = direct_counts(gateway, canvas_id)

        assert duplicate_status == 409, duplicate_status
        assert archive_clone["status"] == "archived"
        assert blocked_status == 409, blocked_status
        assert state["canvas"]["canvas_id"] == canvas_id
        assert state["counters"]["cameras"] == 1
        assert state["counters"]["canvas_objects"] == 1
        assert direct["active_cameras"] == 1
        assert direct["archived_cameras"] == 1
        assert state["cameras"][0]["camera_code"] == "CAM-01"

        print(json.dumps({
            "status": "ok",
            "canvas_id": canvas_id,
            "camera_id": camera_id,
            "clone_id": clone_id,
            "duplicate_status": duplicate_status,
            "blocked_archive_status": blocked_status,
            "state_counters": state["counters"],
            "direct": direct,
        }, ensure_ascii=False, indent=2, default=str))
    finally:
        cleanup(gateway)


def direct_counts(gateway: OracleGateway, canvas_id: int) -> dict[str, int]:
    rows = gateway.fetch_all(
        """
        select 'active_cameras' key, count(*) value
          from RRL_WAREHOUSE_MAP_CAMERA
         where CANVAS_ID = :canvas_id
           and ACTIVE = 1
        union all
        select 'archived_cameras', count(*)
          from RRL_WAREHOUSE_MAP_CAMERA
         where CANVAS_ID = :canvas_id
           and ACTIVE = 0
           and STATUS = 'ARCHIVED'
        union all
        select 'objects', count(*)
          from RRL_WAREHOUSE_MAP_OBJECT
         where CANVAS_ID = :canvas_id
           and ACTIVE = 1
        """,
        {"canvas_id": canvas_id},
    )
    return {str(row["key"]): int(row["value"] or 0) for row in rows}


def cleanup(gateway: OracleGateway) -> None:
    statements: list[tuple[str, dict[str, Any]]] = [
        ("delete from RRL_WAREHOUSE_MAP_CAMERA_LINK where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_PASSAGE where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_OBJECT where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CAMERA where CREATED_BY = :created_by or UPDATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WARES where ID = :ware_id", {"ware_id": WARE_ID}),
    ]
    for sql, params in statements:
        gateway.execute(sql, params)


def get_json(path: str) -> Any:
    request = urllib.request.Request(
        f"{base_url()}{path}",
        headers={"Authorization": f"Basic {auth_token()}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
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
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def post_expect_error(path: str, payload: dict[str, Any]) -> int:
    try:
        post_json(path, payload)
    except urllib.error.HTTPError as exc:
        exc.read()
        return int(exc.code)
    raise AssertionError(f"Expected HTTP error for {path}")


def base_url() -> str:
    return os.getenv("WAREHOUSE_MAP_API_BASE_URL", "http://127.0.0.1:8088").rstrip("/")


def auth_token() -> str:
    username = os.getenv("WAREHOUSE_MAP_API_USER", "admin")
    password = os.getenv("WAREHOUSE_MAP_API_PASSWORD", "admin123")
    return base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")


if __name__ == "__main__":
    main()
