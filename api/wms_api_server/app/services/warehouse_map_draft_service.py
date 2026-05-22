from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    WarehouseMapBulkRoleRequest,
    WarehouseMapDraftCellsPatchRequest,
    WarehouseMapDraftCreateRequest,
    WarehouseMapDraftLoadFromDbRequest,
    WarehouseMapDraftMetadataPatchRequest,
    WarehouseMapDraftOraclePublishRequest,
    WarehouseMapDraftProjectionSaveRequest,
    WarehouseMapDraftRouteBuildRequest,
    WarehouseMapDraftRoutePatchRequest,
    WarehouseMapDraftRouteSaveToDbRequest,
    WarehouseMapDraftSaveToDbRequest,
    WarehouseMapPickFaceAddressRequest,
    WarehouseMapGrid,
    WarehouseMapSelectionRequest,
    WarehouseMapSmallPickFaceGenerateRequest,
    WarehouseMapSmallPickFacePatchRequest,
    WarehouseMapSmallPickFaceRenumberRequest,
    WarehouseMapStorageSlotGenerateRequest,
    WarehouseMapStorageSlotPatchRequest,
)


ROLE_ORDER = ["PICK_FACE", "STORAGE", "TRANSPORT_STAGING", "FILM_WRAP", "GATE", "AISLE", "BLOCKED", "EMPTY", "FRACTIONAL_PICK_FACE", "FRACTIONAL_STORAGE"]
ROLE_INDEX = {role: index for index, role in enumerate(ROLE_ORDER)}
ORACLE_DRAFT_PAYLOAD_VERSION = 1


class WarehouseMapDraftService:
    """Small draft store for the large-map editor before Oracle publish exists."""

    def __init__(self, root_dir: str | None = None, gateway: OracleGateway | None = None) -> None:
        self.root = Path(root_dir or os.getenv("WMS_WAREHOUSE_MAP_DRAFT_DIR", "runtime/warehouse_map_drafts"))
        self.root.mkdir(parents=True, exist_ok=True)
        self.gateway = gateway or OracleGateway()

    def list_drafts(self) -> list[dict]:
        drafts = [self._summary(self._read(path)) for path in sorted(self.root.glob("*.json"))]
        drafts.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        return drafts

    def create_draft(self, request: WarehouseMapDraftCreateRequest, username: str | None) -> dict:
        grid = request.grid
        roles = (
            self._decode_roles(request.roles_base64, grid)
            if request.roles_base64
            else bytearray([ROLE_INDEX["BLOCKED"]]) * self._cell_count(grid)
        )
        draft_id = uuid4().hex
        now = self._now()
        draft = {
            "draft_id": draft_id,
            "draft_name": request.draft_name,
            "status": "DRAFT",
            "grid": grid.model_dump(),
            "roles_base64": self._encode_roles(roles),
            "base_roles_base64": self._encode_roles(roles),
            "role_counts": self._count_roles(roles),
            "revision": 1,
            "draft_metadata": {},
            "base_draft_metadata": {},
            "canvas_objects": [],
            "base_canvas_objects": [],
            "passages": [],
            "base_passages": [],
            "camera_links": [],
            "base_camera_links": [],
            "pick_face_addresses": [],
            "small_pick_faces": [],
            "storage_slots": [],
            "route_rows": [],
            "base_route_rows": [],
            "published_topology": None,
            "created_at": now,
            "updated_at": now,
            "created_by": request.created_by or username,
            "updated_by": request.created_by or username,
        }
        self._write(draft)
        return draft

    def get_draft(self, draft_id: str) -> dict:
        return self._read(self._path(draft_id))

    def load_from_db(self, request: WarehouseMapDraftLoadFromDbRequest, username: str | None) -> dict:
        canvas = self._require_canvas(request.canvas_id)
        payload = self._oracle_draft_payload(canvas)
        if payload is None:
            raise HTTPException(status_code=404, detail="Canvas does not contain warehouse map draft payload.")
        draft = payload.get("draft")
        if not isinstance(draft, dict):
            raise HTTPException(status_code=422, detail="Canvas draft payload is malformed.")
        grid = WarehouseMapGrid(**draft.get("grid", {}))
        roles = self._decode_roles(str(draft.get("roles_base64") or ""), grid)
        now = self._now()
        draft = dict(draft)
        draft["draft_id"] = uuid4().hex
        draft["draft_name"] = request.draft_name or draft.get("draft_name") or canvas.get("canvas_name") or f"Canvas {request.canvas_id}"
        draft["status"] = "DRAFT"
        draft["roles_base64"] = self._encode_roles(roles)
        draft["base_roles_base64"] = draft["roles_base64"]
        draft["role_counts"] = self._count_roles(roles)
        draft["revision"] = 1
        draft["oracle_canvas_id"] = int(request.canvas_id)
        draft["oracle_ware_id"] = int(canvas["ware_id"])
        draft["loaded_from_db_at"] = now
        draft["created_at"] = now
        draft["updated_at"] = now
        draft["created_by"] = request.created_by or username
        draft["updated_by"] = request.created_by or username
        self._reset_base_snapshots(draft)
        self._write(draft)
        return draft

    def save_to_db(self, draft_id: str, request: WarehouseMapDraftSaveToDbRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        validation = self.validate_draft(draft_id)
        if not validation["valid"]:
            raise HTTPException(status_code=409, detail={"message": "Warehouse map draft is not valid.", "validation": validation})
        self._require_warehouse(request.ware_id)
        grid = WarehouseMapGrid(**draft["grid"])
        updated_by = request.updated_by or username
        canvas_id = request.canvas_id or int(draft.get("oracle_canvas_id") or 0) or None
        if canvas_id is not None:
            canvas = self._require_canvas(canvas_id)
            if int(canvas["ware_id"]) != request.ware_id:
                raise HTTPException(status_code=409, detail="Canvas belongs to another warehouse.")
            self._update_canvas_payload(canvas_id, request, draft, grid, updated_by)
        else:
            canvas_id = self._create_canvas_payload(request, draft, grid, updated_by)
        camera_id = self._ensure_default_camera(canvas_id, request.ware_id, request, grid, updated_by)
        draft["oracle_canvas_id"] = canvas_id
        draft["oracle_camera_id"] = camera_id
        draft["oracle_ware_id"] = request.ware_id
        draft["last_db_save_at"] = self._now()
        draft["updated_at"] = draft["last_db_save_at"]
        draft["updated_by"] = updated_by
        self._update_canvas_payload(canvas_id, request, draft, grid, updated_by)
        self._reset_base_snapshots(draft)
        self._write(draft)
        return {
            "draft_id": draft_id,
            "canvas_id": canvas_id,
            "camera_id": camera_id,
            "ware_id": request.ware_id,
            "revision": int(draft.get("revision") or 1),
            "status": "SAVED_TO_DB",
            "validation": validation,
            "role_counts": draft.get("role_counts", {}),
            "route_row_count": len([item for item in draft.get("route_rows", []) if item.get("active", 1)]),
            "saved_at": draft["last_db_save_at"],
        }

    def patch_cells(self, draft_id: str, request: WarehouseMapDraftCellsPatchRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(request.roles_base64, grid)
        draft["roles_base64"] = self._encode_roles(roles)
        draft["role_counts"] = self._count_roles(roles)
        draft["revision"] = int(draft.get("revision") or 1) + 1
        draft["updated_at"] = self._now()
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return draft

    def patch_metadata(self, draft_id: str, request: WarehouseMapDraftMetadataPatchRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        if request.draft_metadata is not None:
            draft["draft_metadata"] = request.draft_metadata
        if request.canvas_objects is not None:
            draft["canvas_objects"] = request.canvas_objects
        if request.passages is not None:
            draft["passages"] = request.passages
        if request.camera_links is not None:
            draft["camera_links"] = request.camera_links
        draft["revision"] = int(draft.get("revision") or 1) + 1
        draft["updated_at"] = self._now()
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return draft

    def diff_draft(self, draft_id: str) -> dict:
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        current = self._decode_roles(draft["roles_base64"], grid)
        base = self._decode_roles(draft.get("base_roles_base64") or draft["roles_base64"], grid)
        changed_by_role: dict[str, int] = {}
        changed_cells = 0
        preview: list[dict] = []
        for index, (old_role_index, new_role_index) in enumerate(zip(base, current)):
            if old_role_index == new_role_index:
                continue
            changed_cells += 1
            role = ROLE_ORDER[new_role_index]
            changed_by_role[role] = changed_by_role.get(role, 0) + 1
            if len(preview) < 20:
                aisle, slot, level = self._cell_from_index(grid, index)
                preview.append({
                    "cell_code": self._physical_cell_code(aisle, slot, level),
                    "from_role": ROLE_ORDER[old_role_index],
                    "to_role": role,
                })
        return {
            "draft_id": draft_id,
            "revision": int(draft.get("revision") or 1),
            "changed_cells": changed_cells,
            "changed_by_role": changed_by_role,
            "draft_metadata_changed": self._json_changed(draft.get("base_draft_metadata") or {}, draft.get("draft_metadata") or {}),
            "canvas_object_count": len(draft.get("canvas_objects") or []),
            "canvas_object_diff_count": self._list_diff_count(draft.get("base_canvas_objects") or [], draft.get("canvas_objects") or []),
            "passage_count": len(draft.get("passages") or []),
            "passage_diff_count": self._list_diff_count(draft.get("base_passages") or [], draft.get("passages") or []),
            "camera_link_count": len(draft.get("camera_links") or []),
            "camera_link_diff_count": self._list_diff_count(draft.get("base_camera_links") or [], draft.get("camera_links") or []),
            "small_pick_face_count": len([item for item in draft.get("small_pick_faces", []) if item.get("active", 1)]),
            "storage_slot_count": len([item for item in draft.get("storage_slots", []) if item.get("active", 1)]),
            "route_row_count": len([item for item in draft.get("route_rows", []) if item.get("active", 1)]),
            "route_row_diff_count": self._list_diff_count(draft.get("base_route_rows") or [], draft.get("route_rows") or []),
            "preview": preview,
        }

    def build_route(self, draft_id: str, request: WarehouseMapDraftRouteBuildRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        grid = WarehouseMapGrid(**draft["grid"])
        selection = self._normalize_selection(request.selection, grid)
        roles = self._decode_roles(draft["roles_base64"], grid)
        ordered_cells = self._route_ordered_cells(selection, request.route_pattern)
        route_rows: list[dict] = []
        skipped_storage = 0
        skipped_non_pick = 0
        sequence = float(request.start_sequence)
        pick_roles = {ROLE_INDEX["PICK_FACE"], ROLE_INDEX["FRACTIONAL_PICK_FACE"]}
        storage_roles = {ROLE_INDEX["STORAGE"], ROLE_INDEX["FRACTIONAL_STORAGE"]}
        for cell in ordered_cells:
            role_value = roles[self._cell_index(grid, cell["aisle"], cell["slot"], cell["level"])]
            if role_value in storage_roles:
                skipped_storage += 1
                continue
            if role_value not in pick_roles:
                skipped_non_pick += 1
                continue
            route_rows.append({
                "route_row_id": uuid4().hex,
                "route_code": request.route_code,
                "route_name": request.route_name,
                "route_pattern": request.route_pattern,
                "cell_code": self._physical_cell_code(cell["aisle"], cell["slot"], cell["level"]),
                "physical_cell": cell,
                "pick_sequence": sequence,
                "slot_kind": "PICK_FACE",
                "active": 1,
            })
            sequence += float(request.step)

        route_rows.sort(key=lambda item: float(item.get("pick_sequence") or 0))
        draft["route_rows"] = route_rows
        draft["route_summary"] = {
            "route_code": request.route_code,
            "route_pattern": request.route_pattern,
            "route_row_count": len(route_rows),
            "skipped_storage_slots": skipped_storage,
            "skipped_non_pick_cells": skipped_non_pick,
        }
        draft["revision"] = int(draft.get("revision") or 1) + 1
        draft["updated_at"] = self._now()
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {
            "draft_id": draft_id,
            "revision": draft["revision"],
            "route_code": request.route_code,
            "route_pattern": request.route_pattern,
            "route_rows": route_rows,
            "route_row_count": len(route_rows),
            "skipped_storage_slots": skipped_storage,
            "skipped_non_pick_cells": skipped_non_pick,
            "updated_at": draft["updated_at"],
        }

    def patch_route(self, draft_id: str, request: WarehouseMapDraftRoutePatchRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        route_rows = self._normalize_route_rows(request.route_rows)
        route_rows.sort(key=lambda item: float(item.get("pick_sequence") or 0))
        draft["route_rows"] = route_rows
        draft["route_summary"] = {
            "route_code": route_rows[0].get("route_code") if route_rows else "DRAFT-PICK",
            "route_pattern": route_rows[0].get("route_pattern") if route_rows else "MANUAL",
            "route_row_count": len([item for item in route_rows if item.get("active", 1)]),
            "manual_patch": 1,
        }
        draft["revision"] = int(draft.get("revision") or 1) + 1
        draft["updated_at"] = self._now()
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {
            "draft_id": draft_id,
            "revision": draft["revision"],
            "route_rows": route_rows,
            "route_row_count": draft["route_summary"]["route_row_count"],
            "updated_at": draft["updated_at"],
        }

    def bulk_role(self, draft_id: str, request: WarehouseMapBulkRoleRequest, username: str | None) -> dict:
        if request.role not in ROLE_INDEX:
            raise HTTPException(status_code=422, detail=f"Unknown warehouse map role: {request.role}")
        selections = self._request_selections(request)
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(draft["roles_base64"], grid)
        changed = 0
        role_value = ROLE_INDEX[request.role]

        for selection in selections:
            normalized = self._normalize_selection(selection, grid)
            for level in range(normalized.level_from, normalized.level_to + 1):
                for slot in range(normalized.slot_from, normalized.slot_to + 1):
                    for aisle in range(normalized.aisle_from, normalized.aisle_to + 1):
                        index = self._cell_index(grid, aisle, slot, level)
                        if roles[index] != role_value:
                            roles[index] = role_value
                            changed += 1

        draft["roles_base64"] = self._encode_roles(roles)
        draft["role_counts"] = self._count_roles(roles)
        draft["updated_at"] = self._now()
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {
            "draft_id": draft_id,
            "role": request.role,
            "changed_cells": changed,
            "selected_cells": sum(self._selection_size(self._normalize_selection(selection, grid)) for selection in selections),
            "role_counts": draft["role_counts"],
            "updated_at": draft["updated_at"],
        }

    def validate_draft(self, draft_id: str) -> dict:
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(draft["roles_base64"], grid)
        errors: list[str] = []
        if len(roles) != self._cell_count(grid):
            errors.append("roles_length_mismatch")
        addresses = draft.get("pick_face_addresses") or []
        codes = [str(item.get("cell_code") or "") for item in addresses if item.get("active", 1)]
        duplicate_codes = sorted({code for code in codes if code and codes.count(code) > 1})
        if duplicate_codes:
            errors.append("duplicate_pick_face_codes")
        for item in addresses:
            index = self._cell_index(grid, int(item["aisle"]), int(item["slot"]), int(item["level"]))
            if roles[index] != ROLE_INDEX["PICK_FACE"]:
                errors.append("pick_face_address_points_to_non_pick_face")
                break
        small_validation = self._validate_small_pick_faces(draft, grid, roles)
        storage_validation = self._validate_storage_slots(draft, grid, roles)
        route_validation = self._validate_route_rows(draft, grid, roles)
        errors.extend(small_validation["errors"])
        errors.extend(storage_validation["errors"])
        errors.extend(route_validation["errors"])
        return {
            "draft_id": draft_id,
            "valid": not errors,
            "error_count": len(errors),
            "errors": errors,
            "duplicate_codes": duplicate_codes,
            "pick_face_address_count": len(addresses),
            "small_pick_face_count": small_validation["small_pick_face_count"],
            "storage_slot_count": storage_validation["storage_slot_count"],
            "duplicate_small_pick_face_codes": small_validation["duplicate_codes"],
            "duplicate_storage_slot_codes": storage_validation["duplicate_codes"],
            "route_row_count": route_validation["route_row_count"],
            "duplicate_route_sequences": route_validation["duplicate_sequences"],
            "duplicate_route_cells": route_validation["duplicate_cells"],
            "route_errors": route_validation["errors"],
            "cell_count": self._cell_count(grid),
            "role_counts": self._count_roles(roles),
        }

    def preview_projection(self, draft_id: str) -> dict:
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(draft["roles_base64"], grid)
        validation = self.validate_draft(draft_id)
        projected_roles = {
            "PICK_FACE",
            "FRACTIONAL_PICK_FACE",
            "STORAGE",
            "FRACTIONAL_STORAGE",
            "TRANSPORT_STAGING",
            "FILM_WRAP",
            "GATE",
            "AISLE",
        }
        cells: list[dict] = []
        role_counts = {role: 0 for role in projected_roles}
        for level in range(1, grid.levels + 1):
            for slot in range(1, grid.slots_per_aisle + 1):
                for aisle in range(1, grid.aisle_count + 1):
                    role = ROLE_ORDER[roles[self._cell_index(grid, aisle, slot, level)]]
                    if role not in projected_roles:
                        continue
                    role_counts[role] += 1
                    if len(cells) < 50:
                        cells.append({
                            "cell_code": self._physical_cell_code(aisle, slot, level),
                            "aisle": aisle,
                            "slot": slot,
                            "level": level,
                            "cell_kind": role,
                            "x_m": round((aisle - 1) * 1.2, 3),
                            "y_m": round((slot - 1) * 0.8, 3),
                            "z_m": round((level - 1) * 1.6, 3),
                        })
        pick_slots = [
            {
                "slot_kind": "PICK_FACE_SLOT",
                "slot_code": item.get("logical_cell_code"),
                "physical_cell_code": item.get("physical_cell_code"),
                "sub_level": item.get("sub_level"),
                "sub_column": item.get("sub_column"),
                "pick_order": item.get("pick_order"),
            }
            for item in draft.get("small_pick_faces", [])
            if item.get("active", 1)
        ]
        storage_slots = [
            {
                "slot_kind": "STORAGE_SLOT",
                "slot_code": item.get("slot_code"),
                "physical_cell_code": item.get("physical_cell_code"),
                "sub_level": item.get("sub_level"),
                "sub_column": item.get("sub_column"),
                "storage_order": item.get("storage_order"),
                "max_pallet_count": item.get("max_pallet_count"),
                "max_weight_kg": item.get("max_weight_kg"),
                "max_volume_m3": item.get("max_volume_m3"),
                "capacity_json": item.get("capacity_json") or {},
            }
            for item in draft.get("storage_slots", [])
            if item.get("active", 1)
        ]
        return {
            "draft_id": draft_id,
            "status": "PREVIEW",
            "publish_ready": validation["valid"],
            "validation": validation,
            "topology_cell_count": sum(role_counts.values()),
            "role_counts": role_counts,
            "pick_face_slot_count": len(pick_slots),
            "storage_slot_count": len(storage_slots),
            "slot_count": len(pick_slots) + len(storage_slots),
            "preview_cells": cells,
            "preview_slots": (pick_slots + storage_slots)[:50],
        }

    def save_projection_to_topology(self, draft_id: str, request: WarehouseMapDraftProjectionSaveRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        validation = self.validate_draft(draft_id)
        if not validation["valid"]:
            raise HTTPException(status_code=409, detail={"message": "Warehouse map draft is not valid.", "validation": validation})
        self._require_warehouse(request.ware_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(draft["roles_base64"], grid)
        topology_id = self._nextval("RRL_WH_TOPOLOGY_SQ")
        topology_code = self._topology_code(request, draft, topology_id)
        updated_by = request.updated_by or username
        camera_id = draft.get("oracle_camera_id")

        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_TOPOLOGY (
              TOPOLOGY_ID, WARE_ID, TOPOLOGY_CODE, TOPOLOGY_NAME, VERSION_NO,
              STATUS, COMMENT_TEXT, CREATED_BY, UPDATED_BY
            ) values (
              :topology_id, :ware_id, :topology_code, :topology_name, 1,
              'DRAFT', :comment_text, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
            )
            """,
            {
                "topology_id": topology_id,
                "ware_id": request.ware_id,
                "topology_code": topology_code,
                "topology_name": request.topology_name or draft.get("draft_name") or f"Topology {topology_id}",
                "comment_text": request.comment_text or f"Projection from warehouse map draft {draft_id}",
                "updated_by": updated_by,
            },
        )

        cell_statements: list[tuple[str, dict]] = []
        projected_cells: dict[str, int] = {}
        role_counts: dict[str, int] = {}
        for cell in self._projection_cells(grid, roles):
            topology_cell_id = self._nextval("RRL_TOPOLOGY_CELL_SQ")
            projected_cells[cell["cell_code"]] = topology_cell_id
            role_counts[cell["cell_kind"]] = role_counts.get(cell["cell_kind"], 0) + 1
            cell_statements.append((
                """
                insert into RRL_TOPOLOGY_CELL (
                  TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE,
                  AISLE_CODE, BAY_NO, LEVEL_NO, POSITION_NO, SIDE_CODE, CELL_KIND,
                  X, Y, Z, WIDTH, DEPTH, HEIGHT, SLOT_LAYER_KIND, WAREHOUSE_MAP_CAMERA_ID,
                  CREATED_BY, UPDATED_BY
                ) values (
                  :topology_cell_id, :topology_id, :ware_id, :cell_code,
                  :aisle_code, :bay_no, :level_no, :position_no, 'CENTER', :cell_kind,
                  :x, :y, :z, 1.2, 0.8, 1.6, :slot_layer_kind, :camera_id,
                  substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                )
                """,
                {
                    "topology_cell_id": topology_cell_id,
                    "topology_id": topology_id,
                    "ware_id": request.ware_id,
                    "cell_code": cell["cell_code"],
                    "aisle_code": cell["aisle_code"],
                    "bay_no": cell["slot"],
                    "level_no": cell["level"],
                    "position_no": cell["aisle"],
                    "cell_kind": cell["cell_kind"],
                    "x": cell["x"],
                    "y": cell["y"],
                    "z": cell["z"],
                    "slot_layer_kind": cell["slot_layer_kind"],
                    "camera_id": camera_id,
                    "updated_by": updated_by,
                },
            ))
        if cell_statements:
            self.gateway.execute_many(cell_statements)

        slot_statements: list[tuple[str, dict]] = []
        slot_counts = {"PICK_FACE_SLOT": 0, "STORAGE_SLOT": 0}
        for slot in self._projection_slot_rows(draft, projected_cells, topology_id, updated_by):
            slot_statements.append((slot["sql"], slot["params"]))
            slot_counts[slot["params"]["slot_kind"]] += 1
        if slot_statements:
            self.gateway.execute_many(slot_statements)

        self.gateway.execute(
            """
            update RRL_WAREHOUSE_MAP_CANVAS
               set TOPOLOGY_ID = :topology_id,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
            """,
            {"topology_id": topology_id, "canvas_id": draft.get("oracle_canvas_id"), "updated_by": updated_by},
        ) if draft.get("oracle_canvas_id") else 0

        draft["oracle_topology_id"] = topology_id
        draft["oracle_topology_code"] = topology_code
        draft["last_projection_save_at"] = self._now()
        draft["updated_at"] = draft["last_projection_save_at"]
        draft["updated_by"] = updated_by
        self._write(draft)
        return {
            "draft_id": draft_id,
            "topology_id": topology_id,
            "topology_code": topology_code,
            "status": "SAVED_TO_TOPOLOGY",
            "topology_cell_count": len(projected_cells),
            "role_counts": role_counts,
            "pick_face_slot_count": slot_counts["PICK_FACE_SLOT"],
            "storage_slot_count": slot_counts["STORAGE_SLOT"],
            "slot_count": slot_counts["PICK_FACE_SLOT"] + slot_counts["STORAGE_SLOT"],
            "validation": validation,
        }

    def save_route_to_db(self, draft_id: str, request: WarehouseMapDraftRouteSaveToDbRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        validation = self.validate_draft(draft_id)
        if not validation["valid"]:
            raise HTTPException(status_code=409, detail={"message": "Warehouse map draft is not valid.", "validation": validation})
        topology_id = request.topology_id or int(draft.get("oracle_topology_id") or 0)
        if topology_id <= 0:
            raise HTTPException(status_code=409, detail="Draft has no saved Oracle topology. Save projection first.")
        topology = self._require_topology(topology_id, request.ware_id)
        canvas_id = draft.get("oracle_canvas_id")
        if not canvas_id:
            raise HTTPException(status_code=409, detail="Draft has no saved Oracle canvas. Save draft to DB first.")
        route_rows = [item for item in draft.get("route_rows", []) if item.get("active", 1)]
        if not route_rows:
            raise HTTPException(status_code=409, detail="Draft route has no active rows.")
        route_code = self._route_code(request, route_rows, topology_id)
        route_name = request.route_name or route_rows[0].get("route_name") or f"Pick route {topology_id}"
        route_pattern = request.route_pattern or route_rows[0].get("route_pattern") or "MANUAL"
        updated_by = request.updated_by or username

        pick_route_id = self._nextval("RRL_PICK_ROUTE_SQ")
        self.gateway.execute(
            """
            insert into RRL_PICK_ROUTE (
              PICK_ROUTE_ID, TOPOLOGY_ID, ROUTE_CODE, ROUTE_NAME, WARE_ID,
              ROUTE_KIND, ROUTE_PATTERN, STRICT_SEQUENCE, STATUS, ACTIVE,
              CREATED_BY, UPDATED_BY
            ) values (
              :pick_route_id, :topology_id, :route_code, :route_name, :ware_id,
              'PICK', :route_pattern, :strict_sequence, 'DRAFT', 1,
              substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
            )
            """,
            {
                "pick_route_id": pick_route_id,
                "topology_id": topology_id,
                "route_code": route_code,
                "route_name": route_name,
                "ware_id": request.ware_id,
                "route_pattern": route_pattern,
                "strict_sequence": request.strict_sequence,
                "updated_by": updated_by,
            },
        )

        lookup = self._topology_route_lookup(topology_id)
        statements: list[tuple[str, dict]] = []
        for path_segment_no, row in enumerate(sorted(route_rows, key=lambda item: float(item.get("pick_sequence") or 0)), start=1):
            route_cell = self._route_row_to_oracle(row, lookup)
            statements.append((
                """
                insert into RRL_PICK_ROUTE_CELL (
                  PICK_ROUTE_CELL_ID, PICK_ROUTE_ID, TOPOLOGY_CELL_ID, CELL_SLOT_ID,
                  WARE_ID, CELL_CODE, PICK_SEQUENCE, AISLE_CODE, SIDE_CODE,
                  BAY_NO, LEVEL_NO, DIRECTION_CODE, VISIT_GROUP_NO, PATH_SEGMENT_NO,
                  DISTANCE_FROM_PREV_M, TURN_COST_SEC, ACTIVE, CREATED_BY, UPDATED_BY
                ) values (
                  RRL_PICK_ROUTE_CELL_SQ.nextval, :pick_route_id, :topology_cell_id, :cell_slot_id,
                  :ware_id, :cell_code, :pick_sequence, :aisle_code, :side_code,
                  :bay_no, :level_no, 'FORWARD', 1, :path_segment_no,
                  0, 0, 1, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                )
                """,
                {
                    "pick_route_id": pick_route_id,
                    "topology_cell_id": route_cell["topology_cell_id"],
                    "cell_slot_id": route_cell["cell_slot_id"],
                    "ware_id": request.ware_id,
                    "cell_code": route_cell["cell_code"],
                    "pick_sequence": float(row.get("pick_sequence") or path_segment_no),
                    "aisle_code": route_cell["aisle_code"],
                    "side_code": route_cell["side_code"],
                    "bay_no": route_cell["bay_no"],
                    "level_no": route_cell["level_no"],
                    "path_segment_no": path_segment_no,
                    "updated_by": updated_by,
                },
            ))
        self.gateway.execute_many(statements)
        oracle_validation = self._validate_oracle_draft(int(canvas_id), pick_route_id)
        if not oracle_validation.get("valid"):
            self.gateway.execute("update RRL_PICK_ROUTE set ACTIVE = 0, STATUS = 'ARCHIVED' where PICK_ROUTE_ID = :pick_route_id", {"pick_route_id": pick_route_id})
            raise HTTPException(status_code=409, detail={"message": "Oracle route validation failed.", "validation": oracle_validation})

        draft["oracle_pick_route_id"] = pick_route_id
        draft["last_route_save_at"] = self._now()
        draft["updated_at"] = draft["last_route_save_at"]
        draft["updated_by"] = updated_by
        self._write(draft)
        return {
            "draft_id": draft_id,
            "pick_route_id": pick_route_id,
            "topology_id": topology_id,
            "topology_code": topology.get("topology_code"),
            "route_code": route_code,
            "route_row_count": len(route_rows),
            "status": "SAVED_TO_DB",
            "oracle_validation": oracle_validation,
        }

    def publish_oracle(self, draft_id: str, request: WarehouseMapDraftOraclePublishRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        self._ensure_revision(draft, request.expected_revision)
        canvas_id = int(request.canvas_id or draft.get("oracle_canvas_id") or 0)
        topology_id = int(request.topology_id or draft.get("oracle_topology_id") or 0)
        pick_route_id = int(request.pick_route_id or draft.get("oracle_pick_route_id") or 0)
        if canvas_id <= 0:
            raise HTTPException(status_code=409, detail="Draft has no saved Oracle canvas. Save draft to DB first.")
        if topology_id <= 0:
            raise HTTPException(status_code=409, detail="Draft has no saved Oracle topology. Save projection first.")
        if pick_route_id <= 0:
            raise HTTPException(status_code=409, detail="Draft has no saved Oracle pick route. Save route to DB first.")

        oracle_validation = self._validate_oracle_draft(canvas_id, pick_route_id)
        if not oracle_validation.get("valid"):
            raise HTTPException(status_code=409, detail={"message": "Oracle route validation failed.", "validation": oracle_validation})

        published_by = request.published_by or username
        try:
            self.gateway.execute_plsql(
                """
                begin
                  RRL_WAREHOUSE_MAP_API.PUBLISH_DRAFT(
                    p_canvas_id => :canvas_id,
                    p_pick_route_id => :pick_route_id,
                    p_published_by => :published_by
                  );
                end;
                """,
                {"canvas_id": canvas_id, "pick_route_id": pick_route_id, "published_by": published_by},
            )
        except Exception as exc:
            raise HTTPException(status_code=409, detail={"message": "Oracle publish failed.", "error": str(exc)}) from exc

        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TOPOLOGY
               set STATUS = 'PUBLISHED',
                   PUBLISHED_AT = systimestamp,
                   PUBLISHED_BY = substr(:published_by, 1, 50),
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:published_by, 1, 50)
             where TOPOLOGY_ID = :topology_id
               and STATUS <> 'ARCHIVED'
            """,
            {"topology_id": topology_id, "published_by": published_by},
        )
        self.gateway.execute(
            """
            update RRL_PICK_ROUTE
               set PUBLISHED_AT = systimestamp,
                   PUBLISHED_BY = substr(:published_by, 1, 50),
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:published_by, 1, 50)
             where PICK_ROUTE_ID = :pick_route_id
            """,
            {"pick_route_id": pick_route_id, "published_by": published_by},
        )

        statuses = self._oracle_publish_status(canvas_id, topology_id, pick_route_id)
        draft["status"] = "PUBLISHED"
        draft["oracle_published_at"] = self._now()
        draft["oracle_published_by"] = published_by
        draft["oracle_publish_validation"] = oracle_validation
        draft["oracle_publish_status"] = statuses
        draft["updated_at"] = draft["oracle_published_at"]
        draft["updated_by"] = published_by
        self._write(draft)
        return {
            "draft_id": draft_id,
            "canvas_id": canvas_id,
            "topology_id": topology_id,
            "pick_route_id": pick_route_id,
            "status": "PUBLISHED",
            "oracle_validation": oracle_validation,
            "oracle_status": statuses,
        }

    def generate_pick_face_addresses(self, draft_id: str, request: WarehouseMapPickFaceAddressRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(draft["roles_base64"], grid)
        selection = self._normalize_selection(request.selection, grid)
        cells = self._ordered_cells(selection, request.anchor_cell.model_dump(), request.focus_cell.model_dump())
        if request.direction == "END_TO_START":
            cells.reverse()

        addresses = [item for item in draft.get("pick_face_addresses", []) if not self._address_inside(item, selection)]
        preview: list[dict] = []
        pick_no = request.start_pick_no
        assigned_count = 0
        for cell in cells:
            index = self._cell_index(grid, cell["aisle"], cell["slot"], cell["level"])
            if roles[index] != ROLE_INDEX["PICK_FACE"]:
                continue
            address = {
                "aisle": cell["aisle"],
                "slot": cell["slot"],
                "level": cell["level"],
                "aisle_no": request.aisle_no,
                "pick_no": pick_no,
                "side": request.side,
                "cell_code": self._format_pick_face_code(request.code_mask, request.aisle_no, pick_no, cell["level"], request.side),
                "anchor_cell": request.anchor_cell.model_dump(),
                "focus_cell": request.focus_cell.model_dump(),
                "direction": request.direction,
                "code_mask": request.code_mask,
                "active": 1,
                "updated_by": request.updated_by or username,
                "updated_at": self._now(),
            }
            addresses.append(address)
            if len(preview) < 3:
                preview.append(address)
            pick_no += request.step
            assigned_count += 1

        draft["pick_face_addresses"] = addresses
        draft["updated_at"] = self._now()
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        tail_preview = addresses[-3:] if len(addresses) > 3 else []
        return {
            "draft_id": draft_id,
            "assigned_count": assigned_count,
            "pick_face_address_count": len(addresses),
            "preview_first": preview,
            "preview_last": tail_preview,
            "updated_at": draft["updated_at"],
        }

    def publish_draft(self, draft_id: str, username: str | None) -> dict:
        validation = self.validate_draft(draft_id)
        if not validation["valid"]:
            raise HTTPException(status_code=409, detail={"message": "Warehouse map draft is not valid.", "validation": validation})
        draft = self.get_draft(draft_id)
        published = {
            "published_topology_id": uuid4().hex,
            "published_at": self._now(),
            "published_by": username,
            "source_draft_id": draft_id,
            "grid": draft["grid"],
            "role_counts": draft.get("role_counts", {}),
            "pick_face_address_count": len(draft.get("pick_face_addresses") or []),
            "small_pick_face_count": len(draft.get("small_pick_faces") or []),
            "storage_slot_count": len(draft.get("storage_slots") or []),
            "route_row_count": len([item for item in draft.get("route_rows", []) if item.get("active", 1)]),
            "route_rows": draft.get("route_rows", [])[:100],
            "cell_count": validation["cell_count"],
            "status": "PUBLISHED",
        }
        draft["status"] = "PUBLISHED"
        draft["published_topology"] = published
        draft["updated_at"] = self._now()
        draft["updated_by"] = username
        self._write(draft)
        self._published_path(published["published_topology_id"]).write_text(json.dumps(published, ensure_ascii=False, indent=2), encoding="utf-8")
        return published

    def generate_small_pick_faces(self, draft_id: str, request: WarehouseMapSmallPickFaceGenerateRequest, username: str | None) -> dict:
        cells = self._small_pick_request_cells(request)
        if request.sub_level_count * request.sub_column_count < request.fraction_cell_count:
            raise HTTPException(status_code=422, detail="sub_level_count * sub_column_count must cover fraction_cell_count.")
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(draft["roles_base64"], grid)
        now = self._now()
        kept = [item for item in draft.get("small_pick_faces", []) if not self._is_same_physical_cell_ref(item, cells)]
        created: list[dict] = []

        for cell in cells:
            self._ensure_cell_inside(grid, cell.aisle, cell.slot, cell.level)
            roles[self._cell_index(grid, cell.aisle, cell.slot, cell.level)] = ROLE_INDEX["FRACTIONAL_PICK_FACE"]
            physical_code = self._physical_cell_code(cell.aisle, cell.slot, cell.level)
            pick_order = request.start_order
            for sub_level, sub_column in self._small_pick_positions(request)[: request.fraction_cell_count]:
                item = {
                    "small_pick_face_id": uuid4().hex,
                    "physical_cell": cell.model_dump(),
                    "physical_cell_code": physical_code,
                    "logical_cell_code": self._format_small_pick_code(request.code_mask, physical_code, cell, sub_level, sub_column, pick_order, request.side),
                    "fraction_type": f"FRACTION_{request.fraction_cell_count}",
                    "fraction_cell_count": request.fraction_cell_count,
                    "sub_level": sub_level,
                    "sub_column": sub_column,
                    "pick_order": pick_order,
                    "side": request.side,
                    "active": 1,
                    "updated_by": request.updated_by or username,
                    "updated_at": now,
                }
                created.append(item)
                pick_order += request.step

        draft["small_pick_faces"] = kept + created
        draft["roles_base64"] = self._encode_roles(roles)
        draft["role_counts"] = self._count_roles(roles)
        draft["updated_at"] = now
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {
            "draft_id": draft_id,
            "created_count": len(created),
            "fraction_cell_count": request.fraction_cell_count,
            "small_pick_face_count": len(draft["small_pick_faces"]),
            "preview": created[:9],
            "role_counts": draft["role_counts"],
            "updated_at": draft["updated_at"],
        }

    def patch_small_pick_face(self, draft_id: str, small_pick_face_id: str, request: WarehouseMapSmallPickFacePatchRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        items = draft.get("small_pick_faces") or []
        target = next((item for item in items if item.get("small_pick_face_id") == small_pick_face_id), None)
        if not target:
            raise HTTPException(status_code=404, detail="Small pick face not found.")
        for key in ("logical_cell_code", "sub_level", "sub_column", "pick_order", "side", "active"):
            value = getattr(request, key)
            if value is not None:
                target[key] = value
        target["updated_by"] = request.updated_by or username
        target["updated_at"] = self._now()
        draft["small_pick_faces"] = items
        draft["updated_at"] = target["updated_at"]
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {"draft_id": draft_id, "small_pick_face": target, "updated_at": draft["updated_at"]}

    def renumber_small_pick_faces(self, draft_id: str, request: WarehouseMapSmallPickFaceRenumberRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        self._ensure_cell_inside(grid, request.physical_cell.aisle, request.physical_cell.slot, request.physical_cell.level)
        items = draft.get("small_pick_faces") or []
        target = [
            item for item in items
            if item.get("active", 1)
            and self._is_same_physical_cell(item, request.physical_cell.aisle, request.physical_cell.slot, request.physical_cell.level)
        ]
        if not target:
            raise HTTPException(status_code=404, detail="Small pick faces for physical cell not found.")
        target.sort(key=lambda item: self._small_pick_sort_key(item, request.order_mode))
        pick_order = request.start_order
        now = self._now()
        for item in target:
            item["pick_order"] = pick_order
            item["updated_by"] = request.updated_by or username
            item["updated_at"] = now
            pick_order += request.step
        draft["small_pick_faces"] = items
        draft["updated_at"] = now
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {"draft_id": draft_id, "renumbered_count": len(target), "small_pick_faces": target, "updated_at": now}

    def generate_storage_slots(self, draft_id: str, request: WarehouseMapStorageSlotGenerateRequest, username: str | None) -> dict:
        if request.fraction_cell_count == 1:
            if request.sub_level_count != 1 or request.sub_column_count != 1:
                raise HTTPException(status_code=422, detail="Default storage split must be 1 x 1.")
        elif request.sub_level_count != 1 or request.sub_column_count != request.fraction_cell_count:
            raise HTTPException(status_code=422, detail="Storage slots can be split only horizontally into 2 or 3 columns.")
        cells = self._small_pick_request_cells(request)
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(draft["roles_base64"], grid)
        now = self._now()
        kept = [item for item in draft.get("storage_slots", []) if not self._is_same_physical_cell_ref(item, cells)]
        created: list[dict] = []

        for cell in cells:
            self._ensure_cell_inside(grid, cell.aisle, cell.slot, cell.level)
            roles[self._cell_index(grid, cell.aisle, cell.slot, cell.level)] = ROLE_INDEX["STORAGE"] if request.fraction_cell_count == 1 else ROLE_INDEX["FRACTIONAL_STORAGE"]
            physical_code = self._physical_cell_code(cell.aisle, cell.slot, cell.level)
            storage_order = request.start_order
            if request.fraction_cell_count > 1:
                for sub_column in range(1, request.fraction_cell_count + 1):
                    item = {
                        "storage_slot_id": uuid4().hex,
                        "physical_cell": cell.model_dump(),
                        "physical_cell_code": physical_code,
                        "slot_code": self._format_storage_slot_code(request.code_mask, physical_code, cell, sub_column, storage_order),
                        "slot_kind": "STORAGE_SLOT",
                        "fraction_type": f"FRACTION_{request.fraction_cell_count}",
                        "fraction_cell_count": request.fraction_cell_count,
                        "sub_level": 1,
                        "sub_column": sub_column,
                        "storage_order": storage_order,
                        "max_pallet_count": 1,
                        "max_weight_kg": None,
                        "max_volume_m3": None,
                        "capacity_json": {},
                        "active": 1,
                        "updated_by": request.updated_by or username,
                        "updated_at": now,
                    }
                    created.append(item)
                    storage_order += request.step

        draft["storage_slots"] = kept + created
        draft["roles_base64"] = self._encode_roles(roles)
        draft["role_counts"] = self._count_roles(roles)
        draft["updated_at"] = now
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {
            "draft_id": draft_id,
            "created_count": len(created),
            "fraction_cell_count": request.fraction_cell_count,
            "storage_slot_count": len(draft["storage_slots"]),
            "preview": created[:9],
            "role_counts": draft["role_counts"],
            "updated_at": draft["updated_at"],
        }

    def patch_storage_slot(self, draft_id: str, storage_slot_id: str, request: WarehouseMapStorageSlotPatchRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        items = draft.get("storage_slots") or []
        target = next((item for item in items if item.get("storage_slot_id") == storage_slot_id), None)
        if not target:
            raise HTTPException(status_code=404, detail="Storage slot not found.")
        for key in ("slot_code", "storage_order", "max_pallet_count", "max_weight_kg", "max_volume_m3", "capacity_json", "active"):
            value = getattr(request, key)
            if value is not None:
                target[key] = value
        target["updated_by"] = request.updated_by or username
        target["updated_at"] = self._now()
        draft["storage_slots"] = items
        draft["updated_at"] = target["updated_at"]
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return {"draft_id": draft_id, "storage_slot": target, "updated_at": draft["updated_at"]}

    def _request_selections(self, request: WarehouseMapBulkRoleRequest) -> list[WarehouseMapSelectionRequest]:
        selections = list(request.selections or [])
        if request.selection:
            selections.append(request.selection)
        if not selections:
            raise HTTPException(status_code=422, detail="At least one selection is required.")
        return selections

    def _normalize_selection(self, selection: WarehouseMapSelectionRequest, grid: WarehouseMapGrid) -> WarehouseMapSelectionRequest:
        aisle_from = min(selection.aisle_from, selection.aisle_to)
        aisle_to = max(selection.aisle_from, selection.aisle_to)
        slot_from = min(selection.slot_from, selection.slot_to)
        slot_to = max(selection.slot_from, selection.slot_to)
        level_from = min(selection.level_from, selection.level_to)
        level_to = max(selection.level_from, selection.level_to)
        if aisle_to > grid.aisle_count or slot_to > grid.slots_per_aisle or level_to > grid.levels:
            raise HTTPException(status_code=422, detail="Selection is outside draft grid.")
        return WarehouseMapSelectionRequest(
            aisle_from=aisle_from,
            aisle_to=aisle_to,
            slot_from=slot_from,
            slot_to=slot_to,
            level_from=level_from,
            level_to=level_to,
        )

    def _summary(self, draft: dict) -> dict:
        return {key: draft.get(key) for key in ("draft_id", "draft_name", "status", "grid", "role_counts", "published_topology", "created_at", "updated_at", "created_by", "updated_by")}

    def _path(self, draft_id: str) -> Path:
        if not draft_id.replace("-", "").replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="Invalid draft id.")
        return self.root / f"{draft_id}.json"

    def _published_path(self, published_topology_id: str) -> Path:
        published_root = self.root / "published"
        published_root.mkdir(parents=True, exist_ok=True)
        return published_root / f"{published_topology_id}.json"

    def _require_warehouse(self, ware_id: int) -> dict:
        rows = self.gateway.fetch_all(
            "select ID WARE_ID, NAME WARE_NAME from RRL_WARES where ID = :ware_id",
            {"ware_id": ware_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Warehouse not found.")
        return rows[0]

    def _require_canvas(self, canvas_id: int) -> dict:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_MAP_CANVAS
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
            """,
            {"canvas_id": canvas_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Warehouse map canvas not found.")
        return rows[0]

    def _require_topology(self, topology_id: int, ware_id: int) -> dict:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_TOPOLOGY
             where TOPOLOGY_ID = :topology_id
               and WARE_ID = :ware_id
               and STATUS <> 'ARCHIVED'
            """,
            {"topology_id": topology_id, "ware_id": ware_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Warehouse topology not found.")
        return rows[0]

    def _oracle_draft_payload(self, canvas: dict) -> dict | None:
        text = canvas.get("renderer_state_json")
        if not text:
            return None
        try:
            payload = json.loads(str(text))
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail="Canvas renderer_state_json is not valid JSON.") from exc
        if payload.get("warehouse_map_draft_payload_version") != ORACLE_DRAFT_PAYLOAD_VERSION:
            return None
        return payload

    def _create_canvas_payload(
        self,
        request: WarehouseMapDraftSaveToDbRequest,
        draft: dict,
        grid: WarehouseMapGrid,
        updated_by: str | None,
    ) -> int:
        canvas_id = self._nextval("RRL_WH_MAP_CANVAS_SQ")
        canvas_code = self._canvas_code(request, draft, canvas_id)
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_MAP_CANVAS (
              CANVAS_ID, WARE_ID, CANVAS_CODE, CANVAS_NAME, VERSION_NO,
              STATUS, RENDERER_KIND, UNIT_CODE, GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M,
              LEVELS, VIEWPORT_JSON, RENDERER_STATE_JSON, COMMENT_TEXT,
              CREATED_BY, UPDATED_BY
            ) values (
              :canvas_id, :ware_id, :canvas_code, :canvas_name, 1,
              'DRAFT', 'CANVAS_2D', 'METER', 1.2, 0.8,
              :levels, :viewport_json, :renderer_state_json, :comment_text,
              substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
            )
            """,
            {
                "canvas_id": canvas_id,
                "ware_id": request.ware_id,
                "canvas_code": canvas_code,
                "canvas_name": request.canvas_name or draft.get("draft_name") or f"Warehouse map draft {canvas_id}",
                "levels": grid.levels,
                "viewport_json": self._json_text({"source": "warehouse_map_draft"}),
                "renderer_state_json": self._json_text(self._db_payload(draft)),
                "comment_text": request.comment_text,
                "updated_by": updated_by,
            },
        )
        return canvas_id

    def _update_canvas_payload(
        self,
        canvas_id: int,
        request: WarehouseMapDraftSaveToDbRequest,
        draft: dict,
        grid: WarehouseMapGrid,
        updated_by: str | None,
    ) -> None:
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_MAP_CANVAS
               set CANVAS_NAME = coalesce(:canvas_name, CANVAS_NAME),
                   GRID_CELL_WIDTH_M = 1.2,
                   GRID_CELL_DEPTH_M = 0.8,
                   LEVELS = :levels,
                   VIEWPORT_JSON = :viewport_json,
                   RENDERER_STATE_JSON = :renderer_state_json,
                   COMMENT_TEXT = coalesce(:comment_text, COMMENT_TEXT),
                   STATUS = case when STATUS = 'PUBLISHED' then STATUS else 'DRAFT' end,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
            """,
            {
                "canvas_id": canvas_id,
                "canvas_name": request.canvas_name,
                "levels": grid.levels,
                "viewport_json": self._json_text({"source": "warehouse_map_draft", "updated_at": self._now()}),
                "renderer_state_json": self._json_text(self._db_payload(draft)),
                "comment_text": request.comment_text,
                "updated_by": updated_by,
            },
        )

    def _ensure_default_camera(
        self,
        canvas_id: int,
        ware_id: int,
        request: WarehouseMapDraftSaveToDbRequest,
        grid: WarehouseMapGrid,
        updated_by: str | None,
    ) -> int:
        rows = self.gateway.fetch_all(
            """
            select CAMERA_ID
              from RRL_WAREHOUSE_MAP_CAMERA
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
             order by CAMERA_ID
            """,
            {"canvas_id": canvas_id},
        )
        width_m = round(grid.aisle_count * 1.2, 3)
        depth_m = round(grid.slots_per_aisle * 0.8, 3)
        height_m = round(grid.levels * 1.6, 3)
        if rows:
            camera_id = int(rows[0]["camera_id"])
            self.gateway.execute(
                """
                update RRL_WAREHOUSE_MAP_CAMERA
                   set WIDTH_M = :width_m,
                       DEPTH_M = :depth_m,
                       HEIGHT_M = :height_m,
                       GRID_CELL_WIDTH_M = 1.2,
                       GRID_CELL_DEPTH_M = 0.8,
                       LEVELS = :levels,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where CAMERA_ID = :camera_id
                """,
                {
                    "camera_id": camera_id,
                    "width_m": width_m,
                    "depth_m": depth_m,
                    "height_m": height_m,
                    "levels": grid.levels,
                    "updated_by": updated_by,
                },
            )
            return camera_id

        camera_id = self._nextval("RRL_WH_MAP_CAMERA_SQ")
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_MAP_CAMERA (
              CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
              ORIGIN_X_M, ORIGIN_Y_M, ORIGIN_Z_M, WIDTH_M, DEPTH_M, HEIGHT_M,
              GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, BOUNDARY_JSON,
              DEFAULT_PASSAGE_WIDTH_M, DEFAULT_AISLE_SPACING_M, STATUS, ACTIVE,
              CREATED_BY, UPDATED_BY
            ) values (
              :camera_id, :canvas_id, :ware_id, :camera_code, :camera_name, 'DRY',
              0, 0, 0, :width_m, :depth_m, :height_m,
              1.2, 0.8, :levels, :boundary_json,
              3, 3.6, 'DRAFT', 1,
              substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
            )
            """,
            {
                "camera_id": camera_id,
                "canvas_id": canvas_id,
                "ware_id": ware_id,
                "camera_code": request.camera_code or "MAIN",
                "camera_name": request.camera_name or "Main camera",
                "width_m": width_m,
                "depth_m": depth_m,
                "height_m": height_m,
                "levels": grid.levels,
                "boundary_json": self._json_text({"grid": grid.model_dump()}),
                "updated_by": updated_by,
            },
        )
        return camera_id

    def _db_payload(self, draft: dict) -> dict:
        return {
            "warehouse_map_draft_payload_version": ORACLE_DRAFT_PAYLOAD_VERSION,
            "saved_at": self._now(),
            "draft": draft,
        }

    def _canvas_code(self, request: WarehouseMapDraftSaveToDbRequest, draft: dict, canvas_id: int) -> str:
        raw = request.canvas_code or draft.get("oracle_canvas_code") or draft.get("draft_name") or f"MAP-{request.ware_id}-{canvas_id}"
        code = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in str(raw).upper()).strip("-_")
        return (code or f"MAP-{request.ware_id}-{canvas_id}")[:80]

    def _topology_code(self, request: WarehouseMapDraftProjectionSaveRequest, draft: dict, topology_id: int) -> str:
        raw = request.topology_code or draft.get("oracle_topology_code") or draft.get("draft_name") or f"MAP-TOPO-{request.ware_id}-{topology_id}"
        code = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in str(raw).upper()).strip("-_")
        return (code or f"MAP-TOPO-{request.ware_id}-{topology_id}")[:80]

    def _route_code(self, request: WarehouseMapDraftRouteSaveToDbRequest, route_rows: list[dict], topology_id: int) -> str:
        raw = request.route_code or route_rows[0].get("route_code") or f"MAP-ROUTE-{topology_id}"
        code = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in str(raw).upper()).strip("-_")
        return (code or f"MAP-ROUTE-{topology_id}")[:80]

    def _projection_cells(self, grid: WarehouseMapGrid, roles: bytearray) -> list[dict]:
        projected_roles = {
            "PICK_FACE": ("PICK_FACE", None),
            "FRACTIONAL_PICK_FACE": ("PICK_FACE", "PICK_FACE_SLOT"),
            "STORAGE": ("STORAGE", None),
            "FRACTIONAL_STORAGE": ("STORAGE", "STORAGE_SLOT"),
            "TRANSPORT_STAGING": ("TRANSPORT_STAGING", None),
            "FILM_WRAP": ("FILM_WRAP", None),
            "GATE": ("GATE", None),
            "AISLE": ("AISLE", None),
        }
        cells: list[dict] = []
        for level in range(1, grid.levels + 1):
            for slot in range(1, grid.slots_per_aisle + 1):
                for aisle in range(1, grid.aisle_count + 1):
                    role = ROLE_ORDER[roles[self._cell_index(grid, aisle, slot, level)]]
                    if role not in projected_roles:
                        continue
                    cell_kind, slot_layer_kind = projected_roles[role]
                    cells.append({
                        "cell_code": self._physical_cell_code(aisle, slot, level),
                        "aisle": aisle,
                        "slot": slot,
                        "level": level,
                        "aisle_code": f"A{aisle:02d}",
                        "cell_kind": cell_kind,
                        "slot_layer_kind": slot_layer_kind,
                        "x": round((aisle - 1) * 1.2, 3),
                        "y": round((slot - 1) * 0.8, 3),
                        "z": round((level - 1) * 1.6, 3),
                    })
        return cells

    def _projection_slot_rows(
        self,
        draft: dict,
        projected_cells: dict[str, int],
        topology_id: int,
        updated_by: str | None,
    ) -> list[dict]:
        rows: list[dict] = []
        pick_indexes: dict[str, int] = {}
        for index, item in enumerate([slot for slot in draft.get("small_pick_faces", []) if slot.get("active", 1)], start=1):
            physical_code = str(item.get("physical_cell_code") or "")
            topology_cell_id = projected_cells.get(physical_code)
            if topology_cell_id is None:
                raise HTTPException(status_code=409, detail=f"Pick slot parent cell is not projected: {physical_code}")
            pick_indexes[physical_code] = pick_indexes.get(physical_code, 0) + 1
            rows.append(self._slot_statement(
                topology_id=topology_id,
                topology_cell_id=topology_cell_id,
                parent_slot_layer_kind="PICK_FACE_SLOT",
                slot_kind="PICK_FACE_SLOT",
                slot_code=str(item.get("logical_cell_code") or f"{physical_code}-P{index}"),
                fraction_count=int(item.get("fraction_cell_count") or 1),
                fraction_index=pick_indexes[physical_code],
                sub_level=item.get("sub_level"),
                sub_column=item.get("sub_column"),
                pick_order=item.get("pick_order"),
                storage_order=None,
                capacity_qty=None,
                capacity_volume_m3=None,
                capacity_weight_kg=None,
                updated_by=updated_by,
            ))
        storage_indexes: dict[str, int] = {}
        for index, item in enumerate([slot for slot in draft.get("storage_slots", []) if slot.get("active", 1)], start=1):
            physical_code = str(item.get("physical_cell_code") or "")
            topology_cell_id = projected_cells.get(physical_code)
            if topology_cell_id is None:
                raise HTTPException(status_code=409, detail=f"Storage slot parent cell is not projected: {physical_code}")
            storage_indexes[physical_code] = storage_indexes.get(physical_code, 0) + 1
            rows.append(self._slot_statement(
                topology_id=topology_id,
                topology_cell_id=topology_cell_id,
                parent_slot_layer_kind="STORAGE_SLOT",
                slot_kind="STORAGE_SLOT",
                slot_code=str(item.get("slot_code") or f"{physical_code}-S{index}"),
                fraction_count=int(item.get("fraction_cell_count") or 1),
                fraction_index=storage_indexes[physical_code],
                sub_level=item.get("sub_level"),
                sub_column=item.get("sub_column"),
                pick_order=None,
                storage_order=item.get("storage_order"),
                capacity_qty=item.get("max_pallet_count"),
                capacity_volume_m3=item.get("max_volume_m3"),
                capacity_weight_kg=item.get("max_weight_kg"),
                updated_by=updated_by,
            ))
        return rows

    def _slot_statement(
        self,
        topology_id: int,
        topology_cell_id: int,
        parent_slot_layer_kind: str,
        slot_kind: str,
        slot_code: str,
        fraction_count: int,
        fraction_index: int,
        sub_level,
        sub_column,
        pick_order,
        storage_order,
        capacity_qty,
        capacity_volume_m3,
        capacity_weight_kg,
        updated_by: str | None,
    ) -> dict:
        return {
            "sql": """
                insert into RRL_TOPOLOGY_CELL_SLOT (
                  CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
                  SLOT_KIND, SLOT_CODE, SLOT_NAME, FRACTION_COUNT, FRACTION_INDEX,
                  SUB_LEVEL_NO, SUB_COLUMN_NO, PICK_ORDER, STORAGE_ORDER,
                  CAPACITY_QTY, CAPACITY_VOLUME_M3, CAPACITY_WEIGHT_KG,
                  CREATED_BY, UPDATED_BY
                ) values (
                  RRL_TOPO_CELL_SLOT_SQ.nextval, :topology_id, :topology_cell_id, :parent_slot_layer_kind,
                  :slot_kind, :slot_code, :slot_code, :fraction_count, :fraction_index,
                  :sub_level, :sub_column, :pick_order, :storage_order,
                  :capacity_qty, :capacity_volume_m3, :capacity_weight_kg,
                  substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                )
            """,
            "params": {
                "topology_id": topology_id,
                "topology_cell_id": topology_cell_id,
                "parent_slot_layer_kind": parent_slot_layer_kind,
                "slot_kind": slot_kind,
                "slot_code": slot_code[:100],
                "fraction_count": fraction_count,
                "fraction_index": fraction_index,
                "sub_level": sub_level,
                "sub_column": sub_column,
                "pick_order": pick_order,
                "storage_order": storage_order,
                "capacity_qty": capacity_qty,
                "capacity_volume_m3": capacity_volume_m3,
                "capacity_weight_kg": capacity_weight_kg,
                "updated_by": updated_by,
            },
        }

    def _topology_route_lookup(self, topology_id: int) -> dict:
        cells = self.gateway.fetch_all(
            """
            select TOPOLOGY_CELL_ID, CELL_CODE, CELL_KIND, AISLE_CODE, SIDE_CODE, BAY_NO, LEVEL_NO
              from RRL_TOPOLOGY_CELL
             where TOPOLOGY_ID = :topology_id
               and ACTIVE = 1
            """,
            {"topology_id": topology_id},
        )
        slots = self.gateway.fetch_all(
            """
            select s.CELL_SLOT_ID,
                   s.TOPOLOGY_CELL_ID,
                   s.SLOT_CODE,
                   s.SLOT_KIND,
                   c.CELL_CODE PHYSICAL_CELL_CODE,
                   c.AISLE_CODE,
                   c.SIDE_CODE,
                   c.BAY_NO,
                   c.LEVEL_NO
              from RRL_TOPOLOGY_CELL_SLOT s
              join RRL_TOPOLOGY_CELL c
                on c.TOPOLOGY_CELL_ID = s.TOPOLOGY_CELL_ID
             where s.TOPOLOGY_ID = :topology_id
               and s.ACTIVE = 1
            """,
            {"topology_id": topology_id},
        )
        return {
            "cells_by_code": {str(item["cell_code"]): item for item in cells},
            "slots_by_code": {str(item["slot_code"]): item for item in slots},
            "pick_slots_by_parent": self._group_pick_slots_by_parent(slots),
        }

    def _group_pick_slots_by_parent(self, slots: list[dict]) -> dict[str, list[dict]]:
        grouped: dict[str, list[dict]] = {}
        for item in slots:
            if item.get("slot_kind") != "PICK_FACE_SLOT":
                continue
            parent = str(item.get("physical_cell_code") or "")
            grouped.setdefault(parent, []).append(item)
        for items in grouped.values():
            items.sort(key=lambda item: str(item.get("slot_code") or ""))
        return grouped

    def _route_row_to_oracle(self, row: dict, lookup: dict) -> dict:
        cell_code = str(row.get("cell_code") or "")
        slot_kind = str(row.get("slot_kind") or "")
        if slot_kind == "STORAGE_SLOT":
            raise HTTPException(status_code=409, detail=f"Route row points to storage slot: {cell_code}")
        if cell_code in lookup["slots_by_code"]:
            slot = lookup["slots_by_code"][cell_code]
            if slot.get("slot_kind") != "PICK_FACE_SLOT":
                raise HTTPException(status_code=409, detail=f"Route row points to non-pick slot: {cell_code}")
            return {
                "topology_cell_id": None,
                "cell_slot_id": slot["cell_slot_id"],
                "cell_code": slot["slot_code"],
                "aisle_code": slot.get("aisle_code"),
                "side_code": slot.get("side_code") or "CENTER",
                "bay_no": slot.get("bay_no"),
                "level_no": slot.get("level_no"),
            }
        if cell_code in lookup["pick_slots_by_parent"]:
            slot = lookup["pick_slots_by_parent"][cell_code][0]
            return {
                "topology_cell_id": None,
                "cell_slot_id": slot["cell_slot_id"],
                "cell_code": slot["slot_code"],
                "aisle_code": slot.get("aisle_code"),
                "side_code": slot.get("side_code") or "CENTER",
                "bay_no": slot.get("bay_no"),
                "level_no": slot.get("level_no"),
            }
        cell = lookup["cells_by_code"].get(cell_code)
        if not cell:
            raise HTTPException(status_code=409, detail=f"Route row cell not found in topology: {cell_code}")
        if cell.get("cell_kind") != "PICK_FACE":
            raise HTTPException(status_code=409, detail=f"Route row points to non-pick cell: {cell_code}")
        return {
            "topology_cell_id": cell["topology_cell_id"],
            "cell_slot_id": None,
            "cell_code": cell["cell_code"],
            "aisle_code": cell.get("aisle_code"),
            "side_code": cell.get("side_code") or "CENTER",
            "bay_no": cell.get("bay_no"),
            "level_no": cell.get("level_no"),
        }

    def _validate_oracle_draft(self, canvas_id: int, pick_route_id: int) -> dict:
        rows = self.gateway.fetch_all(
            """
            select RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT(:canvas_id, :pick_route_id) RESULT
              from dual
            """,
            {"canvas_id": canvas_id, "pick_route_id": pick_route_id},
        )
        text = rows[0].get("result") if rows else "{}"
        try:
            return json.loads(str(text))
        except json.JSONDecodeError:
            return {"valid": False, "raw": str(text)}

    def _oracle_publish_status(self, canvas_id: int, topology_id: int, pick_route_id: int) -> dict:
        rows = self.gateway.fetch_all(
            """
            select c.CANVAS_ID,
                   c.STATUS CANVAS_STATUS,
                   c.ACTIVE CANVAS_ACTIVE,
                   t.TOPOLOGY_ID,
                   t.STATUS TOPOLOGY_STATUS,
                   r.PICK_ROUTE_ID,
                   r.STATUS ROUTE_STATUS,
                   r.ACTIVE ROUTE_ACTIVE,
                   (select count(*)
                      from RRL_PICK_ROUTE_CELL rc
                     where rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID
                       and rc.ACTIVE = 1) ROUTE_ROW_COUNT
              from RRL_WAREHOUSE_MAP_CANVAS c
              join RRL_WAREHOUSE_TOPOLOGY t
                on t.TOPOLOGY_ID = :topology_id
              join RRL_PICK_ROUTE r
                on r.PICK_ROUTE_ID = :pick_route_id
             where c.CANVAS_ID = :canvas_id
            """,
            {"canvas_id": canvas_id, "topology_id": topology_id, "pick_route_id": pick_route_id},
        )
        return rows[0] if rows else {}

    def _json_text(self, value) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    def _nextval(self, sequence_name: str) -> int:
        return self.gateway.call_number_plsql(f"begin select {sequence_name}.nextval into :result from dual; end;", {})

    def _reset_base_snapshots(self, draft: dict) -> None:
        draft["base_roles_base64"] = draft.get("roles_base64")
        draft["base_draft_metadata"] = draft.get("draft_metadata") or {}
        draft["base_canvas_objects"] = list(draft.get("canvas_objects") or [])
        draft["base_passages"] = list(draft.get("passages") or [])
        draft["base_camera_links"] = list(draft.get("camera_links") or [])
        draft["base_route_rows"] = list(draft.get("route_rows") or [])

    def _read(self, path: Path) -> dict:
        if not path.exists():
            raise HTTPException(status_code=404, detail="Warehouse map draft not found.")
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, draft: dict) -> None:
        self._path(draft["draft_id"]).write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")

    def _decode_roles(self, encoded: str, grid: WarehouseMapGrid) -> bytearray:
        try:
            roles = bytearray(base64.b64decode(encoded.encode("ascii"), validate=True))
        except Exception as exc:
            raise HTTPException(status_code=422, detail="roles_base64 is not valid base64.") from exc
        if len(roles) != self._cell_count(grid):
            raise HTTPException(status_code=422, detail="roles_base64 length does not match grid.")
        if any(value >= len(ROLE_ORDER) for value in roles):
            raise HTTPException(status_code=422, detail="roles_base64 contains unknown role indexes.")
        return roles

    def _encode_roles(self, roles: bytearray) -> str:
        return base64.b64encode(bytes(roles)).decode("ascii")

    def _count_roles(self, roles: bytearray) -> dict[str, int]:
        counts = {role: 0 for role in ROLE_ORDER}
        for value in roles:
            counts[ROLE_ORDER[value]] += 1
        return counts

    def _selection_size(self, selection: WarehouseMapSelectionRequest) -> int:
        return (selection.aisle_to - selection.aisle_from + 1) * (selection.slot_to - selection.slot_from + 1) * (selection.level_to - selection.level_from + 1)

    def _cell_count(self, grid: WarehouseMapGrid) -> int:
        return grid.aisle_count * grid.slots_per_aisle * grid.levels

    def _cell_index(self, grid: WarehouseMapGrid, aisle: int, slot: int, level: int) -> int:
        return (level - 1) * grid.aisle_count * grid.slots_per_aisle + (slot - 1) * grid.aisle_count + (aisle - 1)

    def _cell_from_index(self, grid: WarehouseMapGrid, index: int) -> tuple[int, int, int]:
        level_size = grid.aisle_count * grid.slots_per_aisle
        level = index // level_size + 1
        offset = index % level_size
        slot = offset // grid.aisle_count + 1
        aisle = offset % grid.aisle_count + 1
        return aisle, slot, level

    def _ensure_revision(self, draft: dict, expected_revision: int | None) -> None:
        if expected_revision is None:
            return
        current_revision = int(draft.get("revision") or 1)
        if expected_revision != current_revision:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Warehouse map draft revision conflict.",
                    "expected_revision": expected_revision,
                    "current_revision": current_revision,
                },
            )

    def _stable_json(self, value) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _json_changed(self, before, after) -> bool:
        return self._stable_json(before) != self._stable_json(after)

    def _list_diff_count(self, before: list, after: list) -> int:
        before_items = {self._stable_json(item) for item in before}
        after_items = {self._stable_json(item) for item in after}
        return len(before_items.symmetric_difference(after_items))

    def _ensure_cell_inside(self, grid: WarehouseMapGrid, aisle: int, slot: int, level: int) -> None:
        if aisle < 1 or aisle > grid.aisle_count or slot < 1 or slot > grid.slots_per_aisle or level < 1 or level > grid.levels:
            raise HTTPException(status_code=422, detail="Cell is outside draft grid.")

    def _ordered_cells(self, selection: WarehouseMapSelectionRequest, anchor: dict, focus: dict) -> list[dict]:
        aisle_step = 1 if int(anchor["aisle"]) <= int(focus["aisle"]) else -1
        slot_step = 1 if int(anchor["slot"]) <= int(focus["slot"]) else -1
        level_step = 1 if int(anchor["level"]) <= int(focus["level"]) else -1
        aisle_range = range(selection.aisle_from, selection.aisle_to + 1) if aisle_step > 0 else range(selection.aisle_to, selection.aisle_from - 1, -1)
        slot_range = range(selection.slot_from, selection.slot_to + 1) if slot_step > 0 else range(selection.slot_to, selection.slot_from - 1, -1)
        level_range = range(selection.level_from, selection.level_to + 1) if level_step > 0 else range(selection.level_to, selection.level_from - 1, -1)
        return [{"aisle": aisle, "slot": slot, "level": level} for level in level_range for slot in slot_range for aisle in aisle_range]

    def _route_ordered_cells(self, selection: WarehouseMapSelectionRequest, route_pattern: str) -> list[dict]:
        rows: list[dict] = []
        aisle_range = list(range(selection.aisle_from, selection.aisle_to + 1))
        reverse_aisles = list(reversed(aisle_range))
        slot_count = selection.slot_to - selection.slot_from + 1
        for level in range(selection.level_from, selection.level_to + 1):
            for slot_offset, slot in enumerate(range(selection.slot_from, selection.slot_to + 1)):
                if route_pattern == "Z" and slot_offset % 2 == 1:
                    aisles = reverse_aisles
                elif route_pattern == "U_SHAPE" and slot_offset >= slot_count // 2:
                    aisles = reverse_aisles
                elif route_pattern == "P_SHAPE" and slot not in {selection.slot_from, selection.slot_to}:
                    aisles = [selection.aisle_from, selection.aisle_to] if selection.aisle_from != selection.aisle_to else [selection.aisle_from]
                else:
                    aisles = aisle_range
                for aisle in aisles:
                    rows.append({"aisle": aisle, "slot": slot, "level": level})
        return rows

    def _normalize_route_rows(self, rows: list[dict]) -> list[dict]:
        normalized: list[dict] = []
        for row in rows:
            cell = row.get("physical_cell") or {}
            if not all(key in cell for key in ("aisle", "slot", "level")):
                raise HTTPException(status_code=422, detail="Route row physical_cell must include aisle, slot and level.")
            try:
                pick_sequence = float(row.get("pick_sequence"))
                physical_cell = {
                    "aisle": int(cell["aisle"]),
                    "slot": int(cell["slot"]),
                    "level": int(cell["level"]),
                }
            except (TypeError, ValueError) as exc:
                raise HTTPException(status_code=422, detail="Route row has invalid numeric fields.") from exc
            normalized.append({
                "route_row_id": str(row.get("route_row_id") or uuid4().hex),
                "route_code": str(row.get("route_code") or "DRAFT-PICK"),
                "route_name": row.get("route_name"),
                "route_pattern": str(row.get("route_pattern") or "MANUAL"),
                "cell_code": str(row.get("cell_code") or self._physical_cell_code(physical_cell["aisle"], physical_cell["slot"], physical_cell["level"])),
                "physical_cell": physical_cell,
                "pick_sequence": pick_sequence,
                "slot_kind": str(row.get("slot_kind") or "PICK_FACE"),
                "active": int(row.get("active", 1)),
            })
        return normalized

    def _validate_route_rows(self, draft: dict, grid: WarehouseMapGrid, roles: bytearray) -> dict:
        rows = [item for item in draft.get("route_rows", []) if item.get("active", 1)]
        errors: list[str] = []
        sequences = [float(item.get("pick_sequence") or 0) for item in rows]
        duplicate_sequences = sorted({sequence for sequence in sequences if sequences.count(sequence) > 1})
        if duplicate_sequences:
            errors.append("duplicate_route_sequences")
        cells = [str(item.get("cell_code") or "") for item in rows]
        duplicate_cells = sorted({cell for cell in cells if cell and cells.count(cell) > 1})
        if duplicate_cells:
            errors.append("duplicate_route_cells")
        for row in rows:
            cell = row.get("physical_cell") or {}
            try:
                aisle = int(cell.get("aisle"))
                slot = int(cell.get("slot"))
                level = int(cell.get("level"))
            except (TypeError, ValueError):
                errors.append("route_cell_invalid")
                continue
            if aisle < 1 or aisle > grid.aisle_count or slot < 1 or slot > grid.slots_per_aisle or level < 1 or level > grid.levels:
                errors.append("route_cell_outside_grid")
                continue
            if str(row.get("slot_kind") or "") == "STORAGE_SLOT":
                errors.append("route_row_points_to_storage_slot")
                continue
            role = ROLE_ORDER[roles[self._cell_index(grid, aisle, slot, level)]]
            if role in {"STORAGE", "FRACTIONAL_STORAGE"}:
                errors.append("route_row_points_to_storage_cell")
                continue
            if role not in {"PICK_FACE", "FRACTIONAL_PICK_FACE"}:
                errors.append("route_row_points_to_non_pick_cell")
        return {
            "route_row_count": len(rows),
            "duplicate_sequences": duplicate_sequences,
            "duplicate_cells": duplicate_cells,
            "errors": sorted(set(errors)),
        }

    def _address_inside(self, item: dict, selection: WarehouseMapSelectionRequest) -> bool:
        return (
            selection.aisle_from <= int(item.get("aisle", 0)) <= selection.aisle_to
            and selection.slot_from <= int(item.get("slot", 0)) <= selection.slot_to
            and selection.level_from <= int(item.get("level", 0)) <= selection.level_to
        )

    def _format_pick_face_code(self, mask: str, aisle_no: int, pick_no: int, level: int, side: str | None) -> str:
        return mask.format(
            aisle=str(aisle_no).zfill(2),
            pick_no=str(pick_no).zfill(3),
            level=level,
            side=side or "",
        )

    def _small_pick_request_cells(self, request: WarehouseMapSmallPickFaceGenerateRequest):
        cells = list(request.physical_cells or [])
        if request.physical_cell:
            cells.append(request.physical_cell)
        unique = {}
        for cell in cells:
            unique[(cell.aisle, cell.slot, cell.level)] = cell
        if not unique:
            raise HTTPException(status_code=422, detail="At least one physical cell is required.")
        return list(unique.values())

    def _small_pick_positions(self, request: WarehouseMapSmallPickFaceGenerateRequest | WarehouseMapSmallPickFaceRenumberRequest) -> list[tuple[int, int]]:
        sub_level_count = getattr(request, "sub_level_count", 9)
        sub_column_count = getattr(request, "sub_column_count", 9)
        if request.order_mode == "COLUMN_THEN_SUB_LEVEL":
            return [(sub_level, sub_column) for sub_column in range(1, sub_column_count + 1) for sub_level in range(1, sub_level_count + 1)]
        return [(sub_level, sub_column) for sub_level in range(1, sub_level_count + 1) for sub_column in range(1, sub_column_count + 1)]

    def _physical_cell_code(self, aisle: int, slot: int, level: int) -> str:
        return f"A{aisle:02d}-S{slot:03d}-L{level}"

    def _format_small_pick_code(
        self,
        mask: str,
        physical_code: str,
        cell,
        sub_level: int,
        sub_column: int,
        pick_order: int,
        side: str | None,
    ) -> str:
        return mask.format(
            physical_cell=physical_code,
            aisle=str(cell.aisle).zfill(2),
            slot=str(cell.slot).zfill(3),
            level=cell.level,
            sub_level=sub_level,
            sub_column=sub_column,
            pick_order=pick_order,
            side=side or "",
        )

    def _format_storage_slot_code(self, mask: str, physical_code: str, cell, sub_column: int, storage_order: int) -> str:
        return mask.format(
            physical_cell=physical_code,
            aisle=str(cell.aisle).zfill(2),
            slot=str(cell.slot).zfill(3),
            level=cell.level,
            sub_column=sub_column,
            storage_order=storage_order,
        )

    def _is_same_physical_cell_ref(self, item: dict, cells) -> bool:
        return any(self._is_same_physical_cell(item, cell.aisle, cell.slot, cell.level) for cell in cells)

    def _is_same_physical_cell(self, item: dict, aisle: int, slot: int, level: int) -> bool:
        cell = item.get("physical_cell") or {}
        return int(cell.get("aisle", 0)) == aisle and int(cell.get("slot", 0)) == slot and int(cell.get("level", 0)) == level

    def _small_pick_sort_key(self, item: dict, order_mode: str) -> tuple[int, int, int]:
        sub_level = int(item.get("sub_level") or 0)
        sub_column = int(item.get("sub_column") or 0)
        pick_order = int(item.get("pick_order") or 0)
        if order_mode == "COLUMN_THEN_SUB_LEVEL":
            return (sub_column, sub_level, pick_order)
        return (sub_level, sub_column, pick_order)

    def _validate_small_pick_faces(self, draft: dict, grid: WarehouseMapGrid, roles: bytearray) -> dict:
        items = [item for item in draft.get("small_pick_faces", []) if item.get("active", 1)]
        errors: list[str] = []
        codes = [str(item.get("logical_cell_code") or "") for item in items]
        duplicate_codes = sorted({code for code in codes if code and codes.count(code) > 1})
        if duplicate_codes:
            errors.append("duplicate_small_pick_face_codes")

        groups: dict[tuple[int, int, int], list[dict]] = {}
        for item in items:
            cell = item.get("physical_cell") or {}
            try:
                key = (int(cell["aisle"]), int(cell["slot"]), int(cell["level"]))
                self._ensure_cell_inside(grid, key[0], key[1], key[2])
                if roles[self._cell_index(grid, key[0], key[1], key[2])] != ROLE_INDEX["FRACTIONAL_PICK_FACE"]:
                    errors.append("small_pick_face_parent_not_fractional")
                if int(item.get("fraction_cell_count") or 0) < 2 or int(item.get("fraction_cell_count") or 0) > 9:
                    errors.append("invalid_fraction_cell_count")
                if int(item.get("pick_order") or 0) < 1:
                    errors.append("invalid_small_pick_order")
                groups.setdefault(key, []).append(item)
            except (KeyError, TypeError, ValueError, HTTPException):
                errors.append("invalid_small_pick_face_physical_cell")

        for group in groups.values():
            fraction_counts = {int(item.get("fraction_cell_count") or 0) for item in group}
            if len(fraction_counts) != 1 or len(group) != next(iter(fraction_counts)):
                errors.append("small_pick_face_count_mismatch")
            positions = [(int(item.get("sub_level") or 0), int(item.get("sub_column") or 0)) for item in group]
            if len(positions) != len(set(positions)):
                errors.append("duplicate_small_pick_face_position")

        return {
            "errors": sorted(set(errors)),
            "duplicate_codes": duplicate_codes,
            "small_pick_face_count": len(items),
        }

    def _validate_storage_slots(self, draft: dict, grid: WarehouseMapGrid, roles: bytearray) -> dict:
        items = [item for item in draft.get("storage_slots", []) if item.get("active", 1)]
        errors: list[str] = []
        codes = [str(item.get("slot_code") or "") for item in items]
        duplicate_codes = sorted({code for code in codes if code and codes.count(code) > 1})
        if duplicate_codes:
            errors.append("duplicate_storage_slot_codes")

        groups: dict[tuple[int, int, int], list[dict]] = {}
        for item in items:
            cell = item.get("physical_cell") or {}
            try:
                key = (int(cell["aisle"]), int(cell["slot"]), int(cell["level"]))
                self._ensure_cell_inside(grid, key[0], key[1], key[2])
                if roles[self._cell_index(grid, key[0], key[1], key[2])] != ROLE_INDEX["FRACTIONAL_STORAGE"]:
                    errors.append("storage_slot_parent_not_fractional")
                if int(item.get("fraction_cell_count") or 0) not in (2, 3):
                    errors.append("invalid_storage_fraction_cell_count")
                if int(item.get("sub_level") or 0) != 1:
                    errors.append("storage_slot_vertical_split_not_allowed")
                if int(item.get("storage_order") or 0) < 1:
                    errors.append("invalid_storage_order")
                if item.get("max_pallet_count") is not None and float(item.get("max_pallet_count") or 0) < 0:
                    errors.append("invalid_storage_capacity")
                groups.setdefault(key, []).append(item)
            except (KeyError, TypeError, ValueError, HTTPException):
                errors.append("invalid_storage_slot_physical_cell")

        for group in groups.values():
            fraction_counts = {int(item.get("fraction_cell_count") or 0) for item in group}
            if len(fraction_counts) != 1 or len(group) != next(iter(fraction_counts)):
                errors.append("storage_slot_count_mismatch")
            positions = [int(item.get("sub_column") or 0) for item in group]
            if len(positions) != len(set(positions)):
                errors.append("duplicate_storage_slot_position")

        return {
            "errors": sorted(set(errors)),
            "duplicate_codes": duplicate_codes,
            "storage_slot_count": len(items),
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
