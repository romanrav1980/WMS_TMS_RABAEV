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


WARE_EMPTY = -41111
WARE_FULL = -41112
CREATED_BY = "SMOKE_011"


def main() -> None:
    gateway = OracleGateway()
    cleanup(gateway)
    ids: dict[str, int] = {}
    try:
        ids = seed_fixture(gateway)
        full_state = get_json(f"/api/admin/warehouse-map/warehouses/{WARE_FULL}/state")
        empty_state = get_json(f"/api/admin/warehouse-map/warehouses/{WARE_EMPTY}/state")
        canvases = get_json(f"/api/admin/warehouse-map/warehouses/{WARE_FULL}/canvases")
        canvas_state = get_json(f"/api/admin/warehouse-map/canvases/{ids['canvas_id']}")
        warehouse_list = get_json("/api/admin/warehouses?limit=1")
        direct = direct_counts(gateway, ids)

        assert isinstance(warehouse_list, list)
        assert len(canvases) == 1, canvases
        assert full_state["canvas"]["canvas_id"] == ids["canvas_id"]
        assert canvas_state["canvas"]["canvas_id"] == ids["canvas_id"]
        assert empty_state["canvas"] is None
        assert {item["code"] for item in empty_state["warnings"]} >= {"no_canvas", "no_topology"}
        assert full_state["counters"]["cameras"] == direct["cameras"]
        assert full_state["counters"]["canvas_objects"] == direct["canvas_objects"]
        assert full_state["counters"]["passages"] == direct["passages"]
        assert full_state["counters"]["camera_links"] == direct["camera_links"]
        assert full_state["counters"]["topology_cells"] == direct["topology_cells"]
        assert full_state["counters"]["cell_slots"] == direct["cell_slots"]
        assert full_state["counters"]["pick_slots"] == direct["pick_slots"]
        assert full_state["counters"]["storage_slots"] == direct["storage_slots"]
        assert full_state["counters"]["route_rows"] == 1
        assert full_state["counters"]["route_rows_excluded_storage_slots"] == 1
        route_rows = full_state["routes"][0]["route_rows"]
        assert len(route_rows) == 1
        assert route_rows[0]["slot_kind"] == "PICK_FACE_SLOT"
        assert all(row.get("slot_kind") != "STORAGE_SLOT" for row in route_rows)

        print(json.dumps({
            "status": "ok",
            "canvas_id": ids["canvas_id"],
            "topology_id": ids["topology_id"],
            "counters": full_state["counters"],
            "empty_warnings": empty_state["warnings"],
        }, ensure_ascii=False, indent=2, default=str))
    finally:
        cleanup(gateway)


def seed_fixture(gateway: OracleGateway) -> dict[str, int]:
    ids = {
        "topology_id": nextval(gateway, "RRL_WH_TOPOLOGY_SQ"),
        "canvas_id": nextval(gateway, "RRL_WH_MAP_CANVAS_SQ"),
        "camera_a": nextval(gateway, "RRL_WH_MAP_CAMERA_SQ"),
        "camera_b": nextval(gateway, "RRL_WH_MAP_CAMERA_SQ"),
        "pick_cell": nextval(gateway, "RRL_TOPOLOGY_CELL_SQ"),
        "storage_cell": nextval(gateway, "RRL_TOPOLOGY_CELL_SQ"),
        "pick_slot": nextval(gateway, "RRL_TOPO_CELL_SLOT_SQ"),
        "storage_slot": nextval(gateway, "RRL_TOPO_CELL_SLOT_SQ"),
        "route_id": nextval(gateway, "RRL_PICK_ROUTE_SQ"),
        "gate_id": nextval(gateway, "RRL_TOPOLOGY_GATE_SQ"),
    }
    gateway.execute(
        "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
        {"ware_id": WARE_EMPTY, "name": "SMOKE 011 EMPTY", "prefix": "S1E"},
    )
    gateway.execute(
        "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
        {"ware_id": WARE_FULL, "name": "SMOKE 011 FULL", "prefix": "S1F"},
    )
    gateway.execute(
        """
        insert into RRL_WAREHOUSE_TOPOLOGY (
          TOPOLOGY_ID, WARE_ID, TOPOLOGY_CODE, TOPOLOGY_NAME, VERSION_NO, STATUS, CREATED_BY, UPDATED_BY
        ) values (
          :topology_id, :ware_id, 'SMOKE-011-TOPO', 'Smoke topology 011', 1, 'DRAFT', :created_by, :created_by
        )
        """,
        {"topology_id": ids["topology_id"], "ware_id": WARE_FULL, "created_by": CREATED_BY},
    )
    gateway.execute(
        """
        insert into RRL_WAREHOUSE_MAP_CANVAS (
          CANVAS_ID, WARE_ID, TOPOLOGY_ID, CANVAS_CODE, CANVAS_NAME,
          VERSION_NO, STATUS, VIEWPORT_JSON, RENDERER_STATE_JSON, CREATED_BY, UPDATED_BY
        ) values (
          :canvas_id, :ware_id, :topology_id, 'SMOKE-011-CANVAS', 'Smoke canvas 011',
          1, 'DRAFT', :viewport_json, :renderer_state_json, :created_by, :created_by
        )
        """,
        {
            "canvas_id": ids["canvas_id"],
            "ware_id": WARE_FULL,
            "topology_id": ids["topology_id"],
            "viewport_json": '{"zoom":1,"x":0,"y":0}',
            "renderer_state_json": '{"renderer":"CANVAS_2D"}',
            "created_by": CREATED_BY,
        },
    )
    for camera_id, code, origin_x in ((ids["camera_a"], "CAM-A", 0), (ids["camera_b"], "CAM-B", 85)):
        gateway.execute(
            """
            insert into RRL_WAREHOUSE_MAP_CAMERA (
              CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
              ORIGIN_X_M, ORIGIN_Y_M, ORIGIN_Z_M, WIDTH_M, DEPTH_M, HEIGHT_M,
              GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, BOUNDARY_JSON,
              DEFAULT_PASSAGE_WIDTH_M, CREATED_BY, UPDATED_BY
            ) values (
              :camera_id, :canvas_id, :ware_id, :camera_code, :camera_name, 'DRY',
              :origin_x, 0, 0, 80, 120, 12,
              1.2, 0.8, 6, :boundary_json,
              3, :created_by, :created_by
            )
            """,
            {
                "camera_id": camera_id,
                "canvas_id": ids["canvas_id"],
                "ware_id": WARE_FULL,
                "camera_code": code,
                "camera_name": f"Smoke {code}",
                "origin_x": origin_x,
                "boundary_json": '{"shape":"rect"}',
                "created_by": CREATED_BY,
            },
        )
    gateway.execute(
        """
        insert into RRL_WAREHOUSE_MAP_OBJECT (
          MAP_OBJECT_ID, CANVAS_ID, CAMERA_ID, OBJECT_CODE, OBJECT_KIND, OBJECT_NAME,
          X_M, Y_M, Z_M, WIDTH_M, DEPTH_M, HEIGHT_M, GEOMETRY_JSON, STYLE_JSON, CREATED_BY, UPDATED_BY
        ) values (
          RRL_WH_MAP_OBJECT_SQ.nextval, :canvas_id, :camera_id, 'WALL-1', 'WALL', 'Smoke wall',
          1, 1, 0, 10, 0.2, 3, :geometry_json, :style_json, :created_by, :created_by
        )
        """,
        {
            "canvas_id": ids["canvas_id"],
            "camera_id": ids["camera_a"],
            "geometry_json": '{"kind":"segment"}',
            "style_json": '{"stroke":"#333"}',
            "created_by": CREATED_BY,
        },
    )
    gateway.execute(
        """
        insert into RRL_WAREHOUSE_MAP_PASSAGE (
          PASSAGE_ID, CANVAS_ID, CAMERA_ID, PASSAGE_CODE, PASSAGE_NAME, PASSAGE_KIND,
          X1_M, Y1_M, X2_M, Y2_M, WIDTH_M, CREATED_BY, UPDATED_BY
        ) values (
          RRL_WH_MAP_PASSAGE_SQ.nextval, :canvas_id, :camera_id, 'P-1', 'Smoke passage', 'PICK_AISLE',
          0, 0, 0, 30, 3, :created_by, :created_by
        )
        """,
        {"canvas_id": ids["canvas_id"], "camera_id": ids["camera_a"], "created_by": CREATED_BY},
    )
    gateway.execute(
        """
        insert into RRL_WAREHOUSE_MAP_CAMERA_LINK (
          CAMERA_LINK_ID, CANVAS_ID, FROM_CAMERA_ID, TO_CAMERA_ID, LINK_CODE,
          LINK_KIND, DISTANCE_M, DIRECTION_CODE, CREATED_BY, UPDATED_BY
        ) values (
          RRL_WH_MAP_CAM_LINK_SQ.nextval, :canvas_id, :from_camera, :to_camera, 'A-B',
          'CORRIDOR', 5, 'BOTH', :created_by, :created_by
        )
        """,
        {
            "canvas_id": ids["canvas_id"],
            "from_camera": ids["camera_a"],
            "to_camera": ids["camera_b"],
            "created_by": CREATED_BY,
        },
    )
    gateway.execute(
        """
        insert into RRL_TOPOLOGY_GATE (
          TOPOLOGY_GATE_ID, TOPOLOGY_ID, WARE_ID, GATE_CODE, GATE_NAME, GATE_KIND, X, Y, CREATED_BY, UPDATED_BY
        ) values (
          :gate_id, :topology_id, :ware_id, 'G-S11', 'Smoke gate', 'SHIPPING', 10, 40, :created_by, :created_by
        )
        """,
        {"gate_id": ids["gate_id"], "topology_id": ids["topology_id"], "ware_id": WARE_FULL, "created_by": CREATED_BY},
    )
    insert_cell(gateway, ids["pick_cell"], ids["topology_id"], ids["camera_a"], "SMOKE-PICK-011", "PICK_FACE", "PICK_FACE_SLOT", 1)
    insert_cell(gateway, ids["storage_cell"], ids["topology_id"], ids["camera_a"], "SMOKE-STOR-011", "STORAGE", "STORAGE_SLOT", 2)
    insert_slot(gateway, ids["pick_slot"], ids["topology_id"], ids["pick_cell"], "PICK_FACE_SLOT", "SMOKE-PICK-011-A", 10)
    insert_slot(gateway, ids["storage_slot"], ids["topology_id"], ids["storage_cell"], "STORAGE_SLOT", "SMOKE-STOR-011-A", 20)
    gateway.execute(
        """
        insert into RRL_PICK_ROUTE (
          PICK_ROUTE_ID, TOPOLOGY_ID, ROUTE_CODE, ROUTE_NAME, WARE_ID,
          ROUTE_KIND, ROUTE_PATTERN, STRICT_SEQUENCE, STATUS, ACTIVE, CREATED_BY, UPDATED_BY
        ) values (
          :route_id, :topology_id, 'SMOKE-011-ROUTE', 'Smoke route 011', :ware_id,
          'PICK', 'LINEAR', 1, 'DRAFT', 1, :created_by, :created_by
        )
        """,
        {"route_id": ids["route_id"], "topology_id": ids["topology_id"], "ware_id": WARE_FULL, "created_by": CREATED_BY},
    )
    insert_route_row(gateway, ids["route_id"], ids["pick_cell"], ids["pick_slot"], "SMOKE-PICK-011", 1)
    insert_route_row(gateway, ids["route_id"], ids["storage_cell"], ids["storage_slot"], "SMOKE-STOR-011", 2)
    return ids


def insert_cell(
    gateway: OracleGateway,
    cell_id: int,
    topology_id: int,
    camera_id: int,
    cell_code: str,
    cell_kind: str,
    slot_layer_kind: str,
    x: int,
) -> None:
    gateway.execute(
        """
        insert into RRL_TOPOLOGY_CELL (
          TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE, CELL_KIND, SIDE_CODE,
          X, Y, Z, WIDTH, DEPTH, HEIGHT, SLOT_LAYER_KIND, WAREHOUSE_MAP_CAMERA_ID,
          CREATED_BY, UPDATED_BY
        ) values (
          :cell_id, :topology_id, :ware_id, :cell_code, :cell_kind, 'CENTER',
          :x, 1, 0, 1.2, 0.8, 1, :slot_layer_kind, :camera_id,
          :created_by, :created_by
        )
        """,
        {
            "cell_id": cell_id,
            "topology_id": topology_id,
            "ware_id": WARE_FULL,
            "cell_code": cell_code,
            "cell_kind": cell_kind,
            "slot_layer_kind": slot_layer_kind,
            "camera_id": camera_id,
            "x": x,
            "created_by": CREATED_BY,
        },
    )


def insert_slot(
    gateway: OracleGateway,
    slot_id: int,
    topology_id: int,
    cell_id: int,
    slot_kind: str,
    slot_code: str,
    order_value: int,
) -> None:
    pick_order = order_value if slot_kind == "PICK_FACE_SLOT" else None
    storage_order = order_value if slot_kind == "STORAGE_SLOT" else None
    gateway.execute(
        """
        insert into RRL_TOPOLOGY_CELL_SLOT (
          CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
          SLOT_KIND, SLOT_CODE, FRACTION_COUNT, FRACTION_INDEX, SUB_LEVEL_NO, SUB_COLUMN_NO,
          PICK_ORDER, STORAGE_ORDER, CREATED_BY, UPDATED_BY
        ) values (
          :slot_id, :topology_id, :cell_id, :slot_kind,
          :slot_kind, :slot_code, 2, 1, 1, 1,
          :pick_order, :storage_order, :created_by, :created_by
        )
        """,
        {
            "slot_id": slot_id,
            "topology_id": topology_id,
            "cell_id": cell_id,
            "slot_kind": slot_kind,
            "slot_code": slot_code,
            "pick_order": pick_order,
            "storage_order": storage_order,
            "created_by": CREATED_BY,
        },
    )


def insert_route_row(
    gateway: OracleGateway,
    route_id: int,
    cell_id: int,
    slot_id: int,
    cell_code: str,
    sequence: int,
) -> None:
    gateway.execute(
        """
        insert into RRL_PICK_ROUTE_CELL (
          PICK_ROUTE_CELL_ID, PICK_ROUTE_ID, TOPOLOGY_CELL_ID, CELL_SLOT_ID,
          WARE_ID, CELL_CODE, PICK_SEQUENCE, ACTIVE, CREATED_BY, UPDATED_BY
        ) values (
          RRL_PICK_ROUTE_CELL_SQ.nextval, :route_id, :cell_id, :slot_id,
          :ware_id, :cell_code, :pick_sequence, 1, :created_by, :created_by
        )
        """,
        {
            "route_id": route_id,
            "cell_id": cell_id,
            "slot_id": slot_id,
            "ware_id": WARE_FULL,
            "cell_code": cell_code,
            "pick_sequence": sequence,
            "created_by": CREATED_BY,
        },
    )


def direct_counts(gateway: OracleGateway, ids: dict[str, int]) -> dict[str, int]:
    rows = gateway.fetch_all(
        """
        select 'cameras' key, count(*) value from RRL_WAREHOUSE_MAP_CAMERA where CANVAS_ID = :canvas_id and ACTIVE = 1
        union all select 'canvas_objects', count(*) from RRL_WAREHOUSE_MAP_OBJECT where CANVAS_ID = :canvas_id and ACTIVE = 1
        union all select 'passages', count(*) from RRL_WAREHOUSE_MAP_PASSAGE where CANVAS_ID = :canvas_id and ACTIVE = 1
        union all select 'camera_links', count(*) from RRL_WAREHOUSE_MAP_CAMERA_LINK where CANVAS_ID = :canvas_id and ACTIVE = 1
        union all select 'topology_cells', count(*) from RRL_TOPOLOGY_CELL where TOPOLOGY_ID = :topology_id and ACTIVE = 1
        union all select 'cell_slots', count(*) from RRL_TOPOLOGY_CELL_SLOT where TOPOLOGY_ID = :topology_id and ACTIVE = 1
        union all select 'pick_slots', count(*) from RRL_TOPOLOGY_CELL_SLOT where TOPOLOGY_ID = :topology_id and ACTIVE = 1 and SLOT_KIND = 'PICK_FACE_SLOT'
        union all select 'storage_slots', count(*) from RRL_TOPOLOGY_CELL_SLOT where TOPOLOGY_ID = :topology_id and ACTIVE = 1 and SLOT_KIND = 'STORAGE_SLOT'
        """,
        {"canvas_id": ids["canvas_id"], "topology_id": ids["topology_id"]},
    )
    return {str(row["key"]): int(row["value"] or 0) for row in rows}


def cleanup(gateway: OracleGateway) -> None:
    statements: list[tuple[str, dict[str, Any]]] = [
        ("delete from RRL_PICK_ROUTE_CELL where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_PICK_ROUTE where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_TOPOLOGY_GATE where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_TOPOLOGY_CELL where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CAMERA_LINK where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_PASSAGE where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_OBJECT where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CAMERA where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = :created_by", {"created_by": CREATED_BY}),
        ("delete from RRL_WARES where ID in (:ware_empty, :ware_full)", {"ware_empty": WARE_EMPTY, "ware_full": WARE_FULL}),
    ]
    for sql, params in statements:
        gateway.execute(sql, params)


def nextval(gateway: OracleGateway, sequence_name: str) -> int:
    return gateway.call_number_plsql(f"begin select {sequence_name}.nextval into :result from dual; end;", {})


def get_json(path: str) -> Any:
    base_url = os.getenv("WAREHOUSE_MAP_API_BASE_URL", "http://127.0.0.1:8088").rstrip("/")
    username = os.getenv("WAREHOUSE_MAP_API_USER", "admin")
    password = os.getenv("WAREHOUSE_MAP_API_PASSWORD", "admin123")
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    request = urllib.request.Request(
        f"{base_url}{path}",
        headers={"Authorization": f"Basic {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
