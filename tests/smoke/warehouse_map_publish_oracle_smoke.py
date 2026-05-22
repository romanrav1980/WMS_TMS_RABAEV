from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "api" / "wms_api_server"))

from app.oracle_gateway import OracleGateway  # noqa: E402
from app.schemas import (  # noqa: E402
    WarehouseMapBulkRoleRequest,
    WarehouseMapCellRef,
    WarehouseMapDraftCreateRequest,
    WarehouseMapDraftOraclePublishRequest,
    WarehouseMapDraftProjectionSaveRequest,
    WarehouseMapDraftRouteBuildRequest,
    WarehouseMapDraftRouteSaveToDbRequest,
    WarehouseMapDraftSaveToDbRequest,
    WarehouseMapGrid,
    WarehouseMapSelectionRequest,
    WarehouseMapSmallPickFaceGenerateRequest,
)
from app.services.warehouse_map_draft_service import WarehouseMapDraftService  # noqa: E402


WARE_ID = -41226
CREATED_BY = "SMOKE_023"
ROOT_DIR = ROOT / "runtime" / "test-evidence" / "warehouse-map-sprint23-drafts"


def main() -> None:
    gateway = OracleGateway()
    cleanup(gateway)
    if ROOT_DIR.exists():
        shutil.rmtree(ROOT_DIR)
    ROOT_DIR.mkdir(parents=True, exist_ok=True)

    service = WarehouseMapDraftService(root_dir=str(ROOT_DIR), gateway=gateway)
    try:
        gateway.execute(
            "insert into RRL_WARES (ID, NAME, PREFIX) values (:ware_id, :name, :prefix)",
            {"ware_id": WARE_ID, "name": "SMOKE 023 MAP PUBLISH", "prefix": "S23"},
        )
        draft = service.create_draft(
            WarehouseMapDraftCreateRequest(
                draft_name="Smoke 023 publish draft",
                grid=WarehouseMapGrid(aisle_count=4, slots_per_aisle=6, levels=1),
                created_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        service.bulk_role(
            draft["draft_id"],
            WarehouseMapBulkRoleRequest(
                role="PICK_FACE",
                selection=WarehouseMapSelectionRequest(aisle_from=1, aisle_to=2, slot_from=1, slot_to=1, level_from=1, level_to=1),
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        service.generate_small_pick_faces(
            draft["draft_id"],
            WarehouseMapSmallPickFaceGenerateRequest(
                physical_cell=WarehouseMapCellRef(aisle=3, slot=1, level=1),
                fraction_cell_count=2,
                sub_level_count=2,
                sub_column_count=1,
                code_mask="{physical_cell}-P{sub_level}",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        route = service.build_route(
            draft["draft_id"],
            WarehouseMapDraftRouteBuildRequest(
                selection=WarehouseMapSelectionRequest(aisle_from=1, aisle_to=3, slot_from=1, slot_to=1, level_from=1, level_to=1),
                route_code="SMOKE-023-PICK",
                route_name="Smoke 023 route",
                route_pattern="LINEAR",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        saved = service.save_to_db(
            draft["draft_id"],
            WarehouseMapDraftSaveToDbRequest(
                ware_id=WARE_ID,
                canvas_code="SMOKE-023-CANVAS",
                canvas_name="Smoke 023 canvas",
                camera_code="SMOKE-023-MAIN",
                camera_name="Smoke 023 main camera",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        projection = service.save_projection_to_topology(
            draft["draft_id"],
            WarehouseMapDraftProjectionSaveRequest(
                ware_id=WARE_ID,
                topology_code="SMOKE-023-TOPO",
                topology_name="Smoke 023 topology",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        route_save = service.save_route_to_db(
            draft["draft_id"],
            WarehouseMapDraftRouteSaveToDbRequest(
                ware_id=WARE_ID,
                topology_id=int(projection["topology_id"]),
                route_code="SMOKE-023-PICK",
                route_name="Smoke 023 route",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        published = service.publish_oracle(
            draft["draft_id"],
            WarehouseMapDraftOraclePublishRequest(
                canvas_id=int(saved["canvas_id"]),
                topology_id=int(projection["topology_id"]),
                pick_route_id=int(route_save["pick_route_id"]),
                published_by=CREATED_BY,
            ),
            CREATED_BY,
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
            "draft_id": draft["draft_id"],
            "canvas_id": saved["canvas_id"],
            "topology_id": projection["topology_id"],
            "pick_route_id": route_save["pick_route_id"],
            "published": published,
            "direct": direct,
        }, ensure_ascii=False, indent=2, default=str))
    finally:
        cleanup(gateway)


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
