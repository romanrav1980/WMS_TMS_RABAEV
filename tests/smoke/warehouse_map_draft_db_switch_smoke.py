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
    WarehouseMapDraftLoadFromDbRequest,
    WarehouseMapDraftRouteBuildRequest,
    WarehouseMapDraftSaveToDbRequest,
    WarehouseMapGrid,
    WarehouseMapSelectionRequest,
)
from app.services.warehouse_map_draft_service import WarehouseMapDraftService  # noqa: E402


WARE_ID = -41220
CREATED_BY = "SMOKE_020"
ROOT_DIR = ROOT / "runtime" / "test-evidence" / "warehouse-map-sprint20-drafts"


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
            {"ware_id": WARE_ID, "name": "SMOKE 020 MAP DB SWITCH", "prefix": "S20"},
        )
        draft = service.create_draft(
            WarehouseMapDraftCreateRequest(
                draft_name="Smoke 020 draft",
                grid=WarehouseMapGrid(aisle_count=4, slots_per_aisle=6, levels=2),
                created_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        service.bulk_role(
            draft["draft_id"],
            WarehouseMapBulkRoleRequest(
                role="PICK_FACE",
                selection=WarehouseMapSelectionRequest(aisle_from=1, aisle_to=2, slot_from=1, slot_to=4, level_from=1, level_to=1),
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        route = service.build_route(
            draft["draft_id"],
            WarehouseMapDraftRouteBuildRequest(
                selection=WarehouseMapSelectionRequest(aisle_from=1, aisle_to=2, slot_from=1, slot_to=4, level_from=1, level_to=1),
                route_code="SMOKE-020-PICK",
                route_name="Smoke 020 route",
                route_pattern="Z",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        saved = service.save_to_db(
            draft["draft_id"],
            WarehouseMapDraftSaveToDbRequest(
                ware_id=WARE_ID,
                canvas_code="SMOKE-020-CANVAS",
                canvas_name="Smoke 020 canvas",
                camera_code="SMOKE-020-MAIN",
                camera_name="Smoke 020 main camera",
                updated_by=CREATED_BY,
            ),
            CREATED_BY,
        )
        loaded = service.load_from_db(
            WarehouseMapDraftLoadFromDbRequest(canvas_id=int(saved["canvas_id"]), draft_name="Smoke 020 loaded", created_by=CREATED_BY),
            CREATED_BY,
        )
        loaded_validation = service.validate_draft(loaded["draft_id"])
        direct = direct_counts(gateway, int(saved["canvas_id"]))

        assert saved["status"] == "SAVED_TO_DB", saved
        assert saved["route_row_count"] == route["route_row_count"] == 8
        assert loaded["roles_base64"] == service.get_draft(draft["draft_id"])["roles_base64"]
        assert len(loaded.get("route_rows") or []) == 8
        assert loaded_validation["valid"], loaded_validation
        assert direct["canvas_payload_count"] == 1, direct
        assert direct["camera_count"] == 1, direct

        print(json.dumps({
            "status": "ok",
            "draft_id": draft["draft_id"],
            "loaded_draft_id": loaded["draft_id"],
            "canvas_id": saved["canvas_id"],
            "camera_id": saved["camera_id"],
            "route_row_count": saved["route_row_count"],
            "loaded_valid": loaded_validation["valid"],
            "direct": direct,
        }, ensure_ascii=False, indent=2, default=str))
    finally:
        cleanup(gateway)


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
