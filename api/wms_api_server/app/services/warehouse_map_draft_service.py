from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from ..schemas import (
    WarehouseMapBulkRoleRequest,
    WarehouseMapDraftCellsPatchRequest,
    WarehouseMapDraftCreateRequest,
    WarehouseMapPickFaceAddressRequest,
    WarehouseMapGrid,
    WarehouseMapSelectionRequest,
    WarehouseMapSmallPickFaceGenerateRequest,
    WarehouseMapSmallPickFacePatchRequest,
    WarehouseMapSmallPickFaceRenumberRequest,
)


ROLE_ORDER = ["PICK_FACE", "STORAGE", "TRANSPORT_STAGING", "FILM_WRAP", "GATE", "AISLE", "BLOCKED", "EMPTY", "FRACTIONAL_PICK_FACE"]
ROLE_INDEX = {role: index for index, role in enumerate(ROLE_ORDER)}


class WarehouseMapDraftService:
    """Small draft store for the large-map editor before Oracle publish exists."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root = Path(root_dir or os.getenv("WMS_WAREHOUSE_MAP_DRAFT_DIR", "runtime/warehouse_map_drafts"))
        self.root.mkdir(parents=True, exist_ok=True)

    def list_drafts(self) -> list[dict]:
        drafts = [self._summary(self._read(path)) for path in sorted(self.root.glob("*.json"))]
        drafts.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        return drafts

    def create_draft(self, request: WarehouseMapDraftCreateRequest, username: str | None) -> dict:
        grid = request.grid
        roles = self._decode_roles(request.roles_base64, grid) if request.roles_base64 else bytearray(self._cell_count(grid))
        draft_id = uuid4().hex
        now = self._now()
        draft = {
            "draft_id": draft_id,
            "draft_name": request.draft_name,
            "status": "DRAFT",
            "grid": grid.model_dump(),
            "roles_base64": self._encode_roles(roles),
            "role_counts": self._count_roles(roles),
            "pick_face_addresses": [],
            "small_pick_faces": [],
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

    def patch_cells(self, draft_id: str, request: WarehouseMapDraftCellsPatchRequest, username: str | None) -> dict:
        draft = self.get_draft(draft_id)
        grid = WarehouseMapGrid(**draft["grid"])
        roles = self._decode_roles(request.roles_base64, grid)
        draft["roles_base64"] = self._encode_roles(roles)
        draft["role_counts"] = self._count_roles(roles)
        draft["updated_at"] = self._now()
        draft["updated_by"] = request.updated_by or username
        self._write(draft)
        return draft

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
        errors.extend(small_validation["errors"])
        return {
            "draft_id": draft_id,
            "valid": not errors,
            "error_count": len(errors),
            "errors": errors,
            "duplicate_codes": duplicate_codes,
            "pick_face_address_count": len(addresses),
            "small_pick_face_count": small_validation["small_pick_face_count"],
            "duplicate_small_pick_face_codes": small_validation["duplicate_codes"],
            "cell_count": self._cell_count(grid),
            "role_counts": self._count_roles(roles),
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

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
