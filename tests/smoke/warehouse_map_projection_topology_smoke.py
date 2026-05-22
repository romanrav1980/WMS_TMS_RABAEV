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
    WarehouseMapDraftCreateRequest,
    WarehouseMapDraftProjectionSaveRequest,
    WarehouseMapDraftSaveToDbRequest,
    WarehouseMapGrid,
    WarehouseMapSelectionRequest,
    WarehouseMapSmallPickFaceGenerateRequest,
    WarehouseMapStorageSlotGenerateRequest,
    WarehouseMapCellRef,
)
from app.services.warehouse_map_draft_service import WarehouseMapDraftService  # noqa: E402


WARE_ID = -41222
CREATED_BY = "SMOKE_021"
ROOT_DIR = ROOT / "runtime" / "test-evidence" / "warehouse-map-sprint21-drafts"


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
            {"ware_id": WARE_ID, "name": "SMOKE 021 MAP PROJECTION", "prefix": "S21"},
        )
        draft = service.create_draft(
            WarehouseMapDraftCreateRequest(
                draft_name="Smoke 021 projection draft",
                grid=WarehouseMapGrid(aisle_count=4, slots_per_aisle=6, levels=2),
                created_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        service.generate_small_pick_faces(
            draft["draft_id"],
            WarehouseMapSmallPickFaceGenerateRequest(
                physical_cell=WarehouseMapCellRef(aisle=1, slot=1, level=1),
                fraction_cell_count=2,
                sub_level_count=2,
                sub_column_count=1,
                code_mask="{physical_cell}-P{sub_level}",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        service.generate_storage_slots(
            draft["draft_id"],
            WarehouseMapStorageSlotGenerateRequest(
                physical_cell=WarehouseMapCellRef(aisle=2, slot=1, level=1),
                fraction_cell_count=2,
                sub_level_count=1,
                sub_column_count=2,
                code_mask="{physical_cell}-S{sub_column}",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        service.bulk_role(
            draft["draft_id"],
            WarehouseMapBulkRoleRequest(
                role="AISLE",
                selection=WarehouseMapSelectionRequest(aisle_from=3, aisle_to=3, slot_from=1, slot_to=1, level_from=1, level_to=1),
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        saved = service.save_to_db(
            draft["draft_id"],
            WarehouseMapDraftSaveToDbRequest(
                ware_id=WARE_ID,
                canvas_code="SMOKE-021-CANVAS",
                canvas_name="Smoke 021 canvas",
                camera_code="SMOKE-021-MAIN",
                camera_name="Smoke 021 main camera",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        projection = service.save_projection_to_topology(
            draft["draft_id"],
            WarehouseMapDraftProjectionSaveRequest(
                ware_id=WARE_ID,
                topology_code="SMOKE-021-TOPO",
                topology_name="Smoke 021 topology",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        direct = direct_counts(gateway, int(projection["topology_id"]), int(saved["canvas_id"]))

        assert projection["status"] == "SAVED_TO_TOPOLOGY", projection
        assert projection["topology_cell_count"] == 3, projection
        assert projection["pick_face_slot_count"] == 2, projection
        assert projection["storage_slot_count"] == 2, projection
        assert direct["topology_count"] == 1, direct
        assert direct["cell_count"] == 3, direct
        assert direct["pick_slot_count"] == 2, direct
        assert direct["storage_slot_count"] == 2, direct
        assert direct["canvas_topology_link_count"] == 1, direct
        assert direct["storage_slots_in_route"] == 0, direct

        print(json.dumps({
            "status": "ok",
            "draft_id": draft["draft_id"],
            "canvas_id": saved["canvas_id"],
            "topology_id": projection["topology_id"],
            "projection": projection,
            "direct": direct,
        }, ensure_ascii=False, indent=2, default=str))
    finally:
        cleanup(gateway)


def direct_counts(gateway: OracleGateway, topology_id: int, canvas_id: int) -> dict[str, int]:
    rows = gateway.fetch_all(
        """
        select 'topology_count' key, count(*) value
          from RRL_WAREHOUSE_TOPOLOGY
         where TOPOLOGY_ID = :topology_id
        union all
        select 'cell_count', count(*)
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
