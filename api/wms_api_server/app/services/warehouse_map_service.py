from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    WarehouseMapArchiveRequest,
    WarehouseMapCameraCloneRequest,
    WarehouseMapCameraLinksPatchRequest,
    WarehouseMapCameraCreateRequest,
    WarehouseMapCanvasCreateRequest,
    WarehouseMapObjectsPatchRequest,
    WarehouseMapPassagesPatchRequest,
)


JSON_FIELDS = {
    "viewport_json",
    "renderer_state_json",
    "boundary_json",
    "geometry_json",
    "style_json",
}


class WarehouseMapService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_canvases(self, ware_id: int) -> list[dict[str, Any]]:
        self._require_warehouse(ware_id)
        return self.gateway.fetch_all(
            """
            select c.CANVAS_ID,
                   c.WARE_ID,
                   w.NAME WARE_NAME,
                   c.TOPOLOGY_ID,
                   t.TOPOLOGY_CODE,
                   t.TOPOLOGY_NAME,
                   c.CANVAS_CODE,
                   c.CANVAS_NAME,
                   c.VERSION_NO,
                   c.STATUS,
                   c.RENDERER_KIND,
                   c.UNIT_CODE,
                   c.GRID_CELL_WIDTH_M,
                   c.GRID_CELL_DEPTH_M,
                   c.LEVELS,
                   c.ACTIVE,
                   c.CREATED_AT,
                   c.UPDATED_AT,
                   c.PUBLISHED_AT,
                   (select count(*)
                      from RRL_WAREHOUSE_MAP_CAMERA cam
                     where cam.CANVAS_ID = c.CANVAS_ID
                       and cam.ACTIVE = 1) CAMERA_COUNT,
                   (select count(*)
                      from RRL_WAREHOUSE_MAP_OBJECT obj
                     where obj.CANVAS_ID = c.CANVAS_ID
                       and obj.ACTIVE = 1) OBJECT_COUNT,
                   (select count(*)
                      from RRL_WAREHOUSE_MAP_PASSAGE p
                     where p.CANVAS_ID = c.CANVAS_ID
                       and p.ACTIVE = 1) PASSAGE_COUNT,
                   (select count(*)
                      from RRL_WAREHOUSE_MAP_CAMERA_LINK l
                     where l.CANVAS_ID = c.CANVAS_ID
                       and l.ACTIVE = 1) CAMERA_LINK_COUNT
              from RRL_WAREHOUSE_MAP_CANVAS c
              left join RRL_WARES w
                on w.ID = c.WARE_ID
              left join RRL_WAREHOUSE_TOPOLOGY t
                on t.TOPOLOGY_ID = c.TOPOLOGY_ID
             where c.WARE_ID = :ware_id
               and c.ACTIVE = 1
             order by case c.STATUS
                        when 'PUBLISHED' then 1
                        when 'VALIDATED' then 2
                        when 'DRAFT' then 3
                        else 9
                      end,
                      c.VERSION_NO desc,
                      c.CANVAS_ID desc
            """,
            {"ware_id": ware_id},
        )

    def get_warehouse_state(self, ware_id: int, canvas_id: int | None = None) -> dict[str, Any]:
        warehouse = self._require_warehouse(ware_id)
        canvas = self._select_canvas(ware_id, canvas_id)
        if canvas_id is not None and canvas is None:
            raise HTTPException(status_code=404, detail="Warehouse map canvas not found for warehouse.")
        topology = self._select_topology(ware_id, canvas)
        return self._state(warehouse, canvas, topology)

    def get_canvas_state(self, canvas_id: int) -> dict[str, Any]:
        canvas = self._canvas(canvas_id)
        if not canvas:
            raise HTTPException(status_code=404, detail="Warehouse map canvas not found.")
        warehouse = self._require_warehouse(int(canvas["ware_id"]))
        topology = self._select_topology(int(canvas["ware_id"]), canvas)
        return self._state(warehouse, canvas, topology)

    def create_canvas(self, ware_id: int, request: WarehouseMapCanvasCreateRequest, username: str | None) -> dict[str, Any]:
        self._require_warehouse(ware_id)
        if request.topology_id is not None:
            self._require_topology_for_warehouse(ware_id, request.topology_id)
        canvas_id = self._nextval("RRL_WH_MAP_CANVAS_SQ")
        canvas_code = _clean_code(request.canvas_code) or f"MAP-{ware_id}-{canvas_id}"
        if self._canvas_code_exists(ware_id, canvas_code):
            raise HTTPException(status_code=409, detail={"message": "Canvas code already exists.", "field": "canvas_code"})
        created_by = request.created_by or username
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_MAP_CANVAS (
              CANVAS_ID, WARE_ID, TOPOLOGY_ID, CANVAS_CODE, CANVAS_NAME,
              VERSION_NO, STATUS, RENDERER_KIND, UNIT_CODE, GRID_CELL_WIDTH_M,
              GRID_CELL_DEPTH_M, LEVELS, VIEWPORT_JSON, RENDERER_STATE_JSON,
              COMMENT_TEXT, CREATED_BY, UPDATED_BY
            ) values (
              :canvas_id, :ware_id, :topology_id, :canvas_code, :canvas_name,
              1, 'DRAFT', 'CANVAS_2D', 'METER', :grid_cell_width_m,
              :grid_cell_depth_m, :levels, :viewport_json, :renderer_state_json,
              :comment_text, :created_by, :created_by
            )
            """,
            {
                "canvas_id": canvas_id,
                "ware_id": ware_id,
                "topology_id": request.topology_id,
                "canvas_code": canvas_code,
                "canvas_name": request.canvas_name or f"Карта склада {ware_id}",
                "grid_cell_width_m": request.grid_cell_width_m,
                "grid_cell_depth_m": request.grid_cell_depth_m,
                "levels": request.levels,
                "viewport_json": _json_text(request.viewport_json),
                "renderer_state_json": _json_text(request.renderer_state_json),
                "comment_text": request.comment_text,
                "created_by": created_by,
            },
        )
        return self.get_canvas_state(canvas_id)

    def archive_canvas(self, canvas_id: int, request: WarehouseMapArchiveRequest, username: str | None) -> dict[str, Any]:
        canvas = self._require_canvas(canvas_id)
        updated_by = request.updated_by or username
        topology_id = canvas.get("topology_id")
        with self.gateway.transaction("WAREHOUSE_MAP_CANVAS_ARCHIVE") as cursor:
            cursor.execute(
                """
                update RRL_WAREHOUSE_MAP_CAMERA_LINK
                   set ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where CANVAS_ID = :canvas_id
                   and ACTIVE = 1
                """,
                {"canvas_id": canvas_id, "updated_by": updated_by},
            )
            cursor.execute(
                """
                update RRL_WAREHOUSE_MAP_PASSAGE
                   set ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where CANVAS_ID = :canvas_id
                   and ACTIVE = 1
                """,
                {"canvas_id": canvas_id, "updated_by": updated_by},
            )
            cursor.execute(
                """
                update RRL_WAREHOUSE_MAP_OBJECT
                   set ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where CANVAS_ID = :canvas_id
                   and ACTIVE = 1
                """,
                {"canvas_id": canvas_id, "updated_by": updated_by},
            )
            cursor.execute(
                """
                update RRL_WAREHOUSE_MAP_CAMERA
                   set STATUS = 'ARCHIVED',
                       ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where CANVAS_ID = :canvas_id
                   and ACTIVE = 1
                """,
                {"canvas_id": canvas_id, "updated_by": updated_by},
            )
            if topology_id is not None:
                cursor.execute(
                    """
                    update RRL_PICK_ROUTE
                       set STATUS = 'ARCHIVED',
                           ACTIVE = 0,
                           UPDATED_AT = sysdate,
                           UPDATED_BY = substr(:updated_by, 1, 50)
                     where TOPOLOGY_ID = :topology_id
                       and ROUTE_KIND = 'PICK'
                       and ACTIVE = 1
                    """,
                    {"topology_id": topology_id, "updated_by": updated_by},
                )
                cursor.execute(
                    """
                    update RRL_WAREHOUSE_TOPOLOGY
                       set STATUS = 'ARCHIVED',
                           UPDATED_AT = systimestamp,
                           UPDATED_BY = substr(:updated_by, 1, 50)
                     where TOPOLOGY_ID = :topology_id
                       and STATUS <> 'ARCHIVED'
                    """,
                    {"topology_id": topology_id, "updated_by": updated_by},
                )
            cursor.execute(
                """
                update RRL_WAREHOUSE_MAP_CANVAS
                   set STATUS = 'ARCHIVED',
                       ACTIVE = 0,
                       COMMENT_TEXT = substr(
                         coalesce(COMMENT_TEXT || chr(10), '') ||
                         '[ARCHIVED] ' || coalesce(:reason, 'warehouse map canvas archive'),
                         1,
                         1000
                       ),
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where CANVAS_ID = :canvas_id
                   and ACTIVE = 1
                """,
                {"canvas_id": canvas_id, "reason": request.reason, "updated_by": updated_by},
            )
        return {
            "canvas_id": canvas_id,
            "topology_id": int(topology_id) if topology_id is not None else None,
            "status": "ARCHIVED",
            "active": 0,
        }

    def create_camera(self, canvas_id: int, request: WarehouseMapCameraCreateRequest, username: str | None) -> dict[str, Any]:
        canvas = self._require_canvas(canvas_id)
        camera_id = self._nextval("RRL_WH_MAP_CAMERA_SQ")
        camera_code = _clean_code(request.camera_code)
        if not camera_code:
            raise HTTPException(status_code=422, detail="camera_code is required.")
        if self._camera_code_exists(canvas_id, camera_code):
            raise HTTPException(status_code=409, detail={"message": "Camera code already exists.", "field": "camera_code"})
        created_by = request.created_by or username
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_MAP_CAMERA (
              CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
              ORIGIN_X_M, ORIGIN_Y_M, ORIGIN_Z_M, WIDTH_M, DEPTH_M, HEIGHT_M,
              GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, BOUNDARY_JSON,
              DEFAULT_PASSAGE_WIDTH_M, DEFAULT_AISLE_SPACING_M, STATUS, ACTIVE,
              CREATED_BY, UPDATED_BY
            ) values (
              :camera_id, :canvas_id, :ware_id, :camera_code, :camera_name, :camera_kind,
              :origin_x_m, :origin_y_m, :origin_z_m, :width_m, :depth_m, :height_m,
              :grid_cell_width_m, :grid_cell_depth_m, :levels, :boundary_json,
              :default_passage_width_m, :default_aisle_spacing_m, 'DRAFT', 1,
              :created_by, :created_by
            )
            """,
            {
                "camera_id": camera_id,
                "canvas_id": canvas_id,
                "ware_id": canvas["ware_id"],
                "camera_code": camera_code,
                "camera_name": request.camera_name.strip(),
                "camera_kind": request.camera_kind,
                "origin_x_m": request.origin_x_m,
                "origin_y_m": request.origin_y_m,
                "origin_z_m": request.origin_z_m,
                "width_m": request.width_m,
                "depth_m": request.depth_m,
                "height_m": request.height_m,
                "grid_cell_width_m": request.grid_cell_width_m,
                "grid_cell_depth_m": request.grid_cell_depth_m,
                "levels": request.levels,
                "boundary_json": _json_text(request.boundary_json),
                "default_passage_width_m": request.default_passage_width_m,
                "default_aisle_spacing_m": request.default_aisle_spacing_m,
                "created_by": created_by,
            },
        )
        return {"camera": _decode_json_row(self._require_camera(camera_id)), "state": self.get_canvas_state(canvas_id)}

    def clone_camera(self, camera_id: int, request: WarehouseMapCameraCloneRequest, username: str | None) -> dict[str, Any]:
        source = self._require_camera(camera_id)
        canvas_id = int(source["canvas_id"])
        new_camera_id = self._nextval("RRL_WH_MAP_CAMERA_SQ")
        camera_code = _clean_code(request.camera_code) or self._next_camera_copy_code(canvas_id, str(source["camera_code"]))
        if self._camera_code_exists(canvas_id, camera_code):
            raise HTTPException(status_code=409, detail={"message": "Camera code already exists.", "field": "camera_code"})
        created_by = request.created_by or username
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_MAP_CAMERA (
              CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
              ORIGIN_X_M, ORIGIN_Y_M, ORIGIN_Z_M, WIDTH_M, DEPTH_M, HEIGHT_M,
              GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, BOUNDARY_JSON,
              DEFAULT_PASSAGE_WIDTH_M, DEFAULT_AISLE_SPACING_M, STATUS, ACTIVE,
              CREATED_BY, UPDATED_BY
            ) values (
              :camera_id, :canvas_id, :ware_id, :camera_code, :camera_name, :camera_kind,
              :origin_x_m, :origin_y_m, :origin_z_m, :width_m, :depth_m, :height_m,
              :grid_cell_width_m, :grid_cell_depth_m, :levels, :boundary_json,
              :default_passage_width_m, :default_aisle_spacing_m, 'DRAFT', 1,
              :created_by, :created_by
            )
            """,
            {
                "camera_id": new_camera_id,
                "canvas_id": canvas_id,
                "ware_id": source["ware_id"],
                "camera_code": camera_code,
                "camera_name": request.camera_name or f"{source['camera_name']} copy",
                "camera_kind": source["camera_kind"],
                "origin_x_m": request.origin_x_m if request.origin_x_m is not None else source["origin_x_m"],
                "origin_y_m": request.origin_y_m if request.origin_y_m is not None else source["origin_y_m"],
                "origin_z_m": request.origin_z_m if request.origin_z_m is not None else source["origin_z_m"],
                "width_m": source["width_m"],
                "depth_m": source["depth_m"],
                "height_m": source["height_m"],
                "grid_cell_width_m": source["grid_cell_width_m"],
                "grid_cell_depth_m": source["grid_cell_depth_m"],
                "levels": source["levels"],
                "boundary_json": source.get("boundary_json"),
                "default_passage_width_m": source["default_passage_width_m"],
                "default_aisle_spacing_m": source.get("default_aisle_spacing_m"),
                "created_by": created_by,
            },
        )
        return {"camera": _decode_json_row(self._require_camera(new_camera_id)), "state": self.get_canvas_state(canvas_id)}

    def archive_camera(self, camera_id: int, request: WarehouseMapArchiveRequest, username: str | None) -> dict[str, Any]:
        camera = self._require_camera(camera_id)
        dependencies = self._camera_dependency_counts(camera_id)
        blocking = {key: value for key, value in dependencies.items() if value > 0}
        if blocking:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Camera has active dependencies and cannot be archived.",
                    "disabled_reason": "active_dependencies",
                    "dependencies": blocking,
                },
            )
        updated_by = request.updated_by or username
        comment = f"Archived from map UI. {request.reason or ''}".strip()
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_MAP_CAMERA
               set STATUS = 'ARCHIVED',
                   ACTIVE = 0,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = :updated_by
             where CAMERA_ID = :camera_id
            """,
            {"camera_id": camera_id, "updated_by": updated_by},
        )
        return {
            "status": "archived",
            "camera_id": camera_id,
            "canvas_id": camera["canvas_id"],
            "disabled_reason": None,
            "comment": comment,
            "state": self.get_canvas_state(int(camera["canvas_id"])),
        }

    def replace_camera_objects(self, camera_id: int, request: WarehouseMapObjectsPatchRequest, username: str | None) -> dict[str, Any]:
        camera = self._require_camera(camera_id)
        canvas_id = int(camera["canvas_id"])
        updated_by = request.updated_by or username
        statements: list[tuple[str, dict[str, Any]]] = [
            (
                """
                update RRL_WAREHOUSE_MAP_OBJECT
                   set ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = :updated_by
                 where CAMERA_ID = :camera_id
                   and ACTIVE = 1
                """,
                {"camera_id": camera_id, "updated_by": updated_by},
            )
        ]
        for index, item in enumerate(request.objects, start=1):
            object_id = self._nextval("RRL_WH_MAP_OBJECT_SQ")
            statements.append((
                """
                insert into RRL_WAREHOUSE_MAP_OBJECT (
                  MAP_OBJECT_ID, CANVAS_ID, CAMERA_ID, TOPOLOGY_CELL_ID,
                  OBJECT_CODE, OBJECT_KIND, OBJECT_NAME, LEVEL_NO,
                  X_M, Y_M, Z_M, WIDTH_M, DEPTH_M, HEIGHT_M, ANGLE_DEG,
                  GEOMETRY_JSON, STYLE_JSON, ACTIVE, CREATED_BY, UPDATED_BY
                ) values (
                  :map_object_id, :canvas_id, :camera_id, :topology_cell_id,
                  :object_code, :object_kind, :object_name, :level_no,
                  :x_m, :y_m, :z_m, :width_m, :depth_m, :height_m, :angle_deg,
                  :geometry_json, :style_json, 1, :updated_by, :updated_by
                )
                """,
                {
                    "map_object_id": object_id,
                    "canvas_id": canvas_id,
                    "camera_id": camera_id,
                    "topology_cell_id": item.topology_cell_id,
                    "object_code": _clean_code(item.object_code) or f"OBJ-{camera_id}-{index:03d}",
                    "object_kind": item.object_kind,
                    "object_name": item.object_name,
                    "level_no": item.level_no,
                    "x_m": item.x_m,
                    "y_m": item.y_m,
                    "z_m": item.z_m,
                    "width_m": item.width_m,
                    "depth_m": item.depth_m,
                    "height_m": item.height_m,
                    "angle_deg": item.angle_deg,
                    "geometry_json": _json_text(item.geometry_json),
                    "style_json": _json_text(item.style_json),
                    "updated_by": updated_by,
                },
            ))
        self.gateway.execute_many(statements)
        return {"camera_id": camera_id, "canvas_id": canvas_id, "object_count": len(request.objects), "state": self.get_canvas_state(canvas_id)}

    def replace_camera_passages(self, camera_id: int, request: WarehouseMapPassagesPatchRequest, username: str | None) -> dict[str, Any]:
        camera = self._require_camera(camera_id)
        canvas_id = int(camera["canvas_id"])
        updated_by = request.updated_by or username
        statements: list[tuple[str, dict[str, Any]]] = [
            (
                """
                update RRL_WAREHOUSE_MAP_PASSAGE
                   set ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = :updated_by
                 where CAMERA_ID = :camera_id
                   and ACTIVE = 1
                """,
                {"camera_id": camera_id, "updated_by": updated_by},
            )
        ]
        for index, item in enumerate(request.passages, start=1):
            passage_id = self._nextval("RRL_WH_MAP_PASSAGE_SQ")
            statements.append((
                """
                insert into RRL_WAREHOUSE_MAP_PASSAGE (
                  PASSAGE_ID, CANVAS_ID, CAMERA_ID, PASSAGE_CODE, PASSAGE_NAME,
                  PASSAGE_KIND, X1_M, Y1_M, Z1_M, X2_M, Y2_M, Z2_M,
                  WIDTH_M, AISLE_SPACING_M, GEOMETRY_JSON, ALLOWED_RESOURCE_MASK,
                  ACTIVE, CREATED_BY, UPDATED_BY
                ) values (
                  :passage_id, :canvas_id, :camera_id, :passage_code, :passage_name,
                  :passage_kind, :x1_m, :y1_m, :z1_m, :x2_m, :y2_m, :z2_m,
                  :width_m, :aisle_spacing_m, :geometry_json, :allowed_resource_mask,
                  1, :updated_by, :updated_by
                )
                """,
                {
                    "passage_id": passage_id,
                    "canvas_id": canvas_id,
                    "camera_id": camera_id,
                    "passage_code": _clean_code(item.passage_code) or f"PASS-{camera_id}-{index:03d}",
                    "passage_name": item.passage_name,
                    "passage_kind": item.passage_kind,
                    "x1_m": item.x1_m,
                    "y1_m": item.y1_m,
                    "z1_m": item.z1_m,
                    "x2_m": item.x2_m,
                    "y2_m": item.y2_m,
                    "z2_m": item.z2_m,
                    "width_m": item.width_m,
                    "aisle_spacing_m": item.aisle_spacing_m,
                    "geometry_json": _json_text(item.geometry_json),
                    "allowed_resource_mask": item.allowed_resource_mask,
                    "updated_by": updated_by,
                },
            ))
        self.gateway.execute_many(statements)
        return {"camera_id": camera_id, "canvas_id": canvas_id, "passage_count": len(request.passages), "state": self.get_canvas_state(canvas_id)}

    def replace_camera_links(self, canvas_id: int, request: WarehouseMapCameraLinksPatchRequest, username: str | None) -> dict[str, Any]:
        self._require_canvas(canvas_id)
        for item in request.camera_links:
            from_camera = self._require_camera(item.from_camera_id)
            to_camera = self._require_camera(item.to_camera_id)
            if int(from_camera["canvas_id"]) != canvas_id or int(to_camera["canvas_id"]) != canvas_id:
                raise HTTPException(status_code=422, detail="Camera link endpoints must belong to the target canvas.")
        updated_by = request.updated_by or username
        statements: list[tuple[str, dict[str, Any]]] = [
            (
                """
                update RRL_WAREHOUSE_MAP_CAMERA_LINK
                   set ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = :updated_by
                 where CANVAS_ID = :canvas_id
                   and ACTIVE = 1
                """,
                {"canvas_id": canvas_id, "updated_by": updated_by},
            )
        ]
        for index, item in enumerate(request.camera_links, start=1):
            link_id = self._nextval("RRL_WH_MAP_CAM_LINK_SQ")
            statements.append((
                """
                insert into RRL_WAREHOUSE_MAP_CAMERA_LINK (
                  CAMERA_LINK_ID, CANVAS_ID, FROM_CAMERA_ID, TO_CAMERA_ID,
                  LINK_CODE, LINK_KIND, FROM_POINT_X_M, FROM_POINT_Y_M, FROM_POINT_Z_M,
                  TO_POINT_X_M, TO_POINT_Y_M, TO_POINT_Z_M, DISTANCE_M, TRAVEL_TIME_SEC,
                  DIRECTION_CODE, ALLOWED_RESOURCE_MASK, ACTIVE, CREATED_BY, UPDATED_BY
                ) values (
                  :camera_link_id, :canvas_id, :from_camera_id, :to_camera_id,
                  :link_code, :link_kind, :from_point_x_m, :from_point_y_m, :from_point_z_m,
                  :to_point_x_m, :to_point_y_m, :to_point_z_m, :distance_m, :travel_time_sec,
                  :direction_code, :allowed_resource_mask, 1, :updated_by, :updated_by
                )
                """,
                {
                    "camera_link_id": link_id,
                    "canvas_id": canvas_id,
                    "from_camera_id": item.from_camera_id,
                    "to_camera_id": item.to_camera_id,
                    "link_code": _clean_code(item.link_code) or f"LINK-{canvas_id}-{index:03d}",
                    "link_kind": item.link_kind,
                    "from_point_x_m": item.from_point_x_m,
                    "from_point_y_m": item.from_point_y_m,
                    "from_point_z_m": item.from_point_z_m,
                    "to_point_x_m": item.to_point_x_m,
                    "to_point_y_m": item.to_point_y_m,
                    "to_point_z_m": item.to_point_z_m,
                    "distance_m": item.distance_m,
                    "travel_time_sec": item.travel_time_sec,
                    "direction_code": item.direction_code,
                    "allowed_resource_mask": item.allowed_resource_mask,
                    "updated_by": updated_by,
                },
            ))
        self.gateway.execute_many(statements)
        return {"canvas_id": canvas_id, "camera_link_count": len(request.camera_links), "state": self.get_canvas_state(canvas_id)}

    def _state(
        self,
        warehouse: dict[str, Any],
        canvas: dict[str, Any] | None,
        topology: dict[str, Any] | None,
    ) -> dict[str, Any]:
        canvas_id = int(canvas["canvas_id"]) if canvas else None
        topology_id = int(topology["topology_id"]) if topology else None
        warnings: list[dict[str, str]] = []
        if canvas is None:
            warnings.append({"code": "no_canvas", "message": "Warehouse has no saved canvas yet."})
        if topology is None:
            warnings.append({"code": "no_topology", "message": "Warehouse has no topology projection yet."})
        elif canvas is not None and canvas.get("topology_id") is None:
            warnings.append({"code": "canvas_without_topology", "message": "Canvas is not linked to a topology yet."})

        cameras = self._cameras(canvas_id)
        camera_links = self._camera_links(canvas_id)
        canvas_objects = self._canvas_objects(canvas_id)
        passages = self._passages(canvas_id)
        zones = self._zones(topology_id)
        aisles = self._aisles(topology_id)
        gates = self._gates(topology_id)
        topology_cells = self._topology_cells(topology_id)
        cell_slots = self._cell_slots(topology_id)
        routes = self._routes(topology_id)
        route_rows = self._route_rows(topology_id)
        excluded_route_rows = self._excluded_storage_route_rows(topology_id)
        route_rows_by_route = _group_by(route_rows, "pick_route_id")
        excluded_by_route = _count_by(excluded_route_rows, "pick_route_id")
        for route in routes:
            route_id = route.get("pick_route_id")
            route["route_rows"] = route_rows_by_route.get(route_id, [])
            route["route_row_count"] = len(route["route_rows"])
            route["excluded_storage_slot_row_count"] = excluded_by_route.get(route_id, 0)

        counters = {
            "canvases": 1 if canvas else 0,
            "cameras": len(cameras),
            "camera_links": len(camera_links),
            "canvas_objects": len(canvas_objects),
            "passages": len(passages),
            "zones": len(zones),
            "aisles": len(aisles),
            "gates": len(gates),
            "topology_cells": len(topology_cells),
            "cell_slots": len(cell_slots),
            "pick_slots": sum(1 for slot in cell_slots if slot.get("slot_kind") == "PICK_FACE_SLOT"),
            "storage_slots": sum(1 for slot in cell_slots if slot.get("slot_kind") == "STORAGE_SLOT"),
            "routes": len(routes),
            "route_rows": len(route_rows),
            "route_rows_excluded_storage_slots": len(excluded_route_rows),
        }

        return {
            "warehouse": warehouse,
            "canvas": _decode_json_row(canvas),
            "topology": topology,
            "cameras": _decode_json_rows(cameras),
            "camera_links": camera_links,
            "canvas_objects": _decode_json_rows(canvas_objects),
            "passages": _decode_json_rows(passages),
            "zones": zones,
            "aisles": aisles,
            "gates": gates,
            "topology_cells": topology_cells,
            "cell_slots": cell_slots,
            "routes": routes,
            "counters": counters,
            "warnings": warnings,
        }

    def _require_warehouse(self, ware_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select ID WARE_ID,
                   NAME WARE_NAME,
                   PREFIX,
                   nvl(FLAG_RAW_MATERIAL, 0) FLAG_RAW_MATERIAL,
                   nvl(FLAG_PRODUCTION, 0) FLAG_PRODUCTION,
                   nvl(FLAG_PRODUCTION_BUFFER, 0) FLAG_PRODUCTION_BUFFER,
                   nvl(FLAG_FINISHED_GOODS, 0) FLAG_FINISHED_GOODS,
                   nvl(MES_ENABLED, 0) MES_ENABLED,
                   DEFAULT_RECEIVE_CELL,
                   DEFAULT_ISSUE_CELL,
                   WARE_COMMENT,
                   OVERFLOW_CELL_NAME,
                   PARENT_WARE_ID,
                   ORD2
              from RRL_WARES
             where ID = :ware_id
            """,
            {"ware_id": ware_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Warehouse not found.")
        return rows[0]

    def _require_topology_for_warehouse(self, ware_id: int, topology_id: int) -> dict[str, Any]:
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
            raise HTTPException(status_code=404, detail="Warehouse topology not found for warehouse.")
        return rows[0]

    def _require_canvas(self, canvas_id: int) -> dict[str, Any]:
        canvas = self._canvas(canvas_id)
        if not canvas:
            raise HTTPException(status_code=404, detail="Warehouse map canvas not found.")
        return canvas

    def _require_camera(self, camera_id: int) -> dict[str, Any]:
        camera = self._camera(camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Warehouse map camera not found.")
        return camera

    def _select_canvas(self, ware_id: int, canvas_id: int | None = None) -> dict[str, Any] | None:
        if canvas_id is not None:
            canvas = self._canvas(canvas_id)
            if canvas and int(canvas["ware_id"]) == ware_id:
                return canvas
            return None
        rows = self.gateway.fetch_all(
            """
            select *
              from (
                select c.*
                  from RRL_WAREHOUSE_MAP_CANVAS c
                 where c.WARE_ID = :ware_id
                   and c.ACTIVE = 1
                 order by case c.STATUS
                            when 'PUBLISHED' then 1
                            when 'VALIDATED' then 2
                            when 'DRAFT' then 3
                            else 9
                          end,
                          c.VERSION_NO desc,
                          c.CANVAS_ID desc
              )
             where rownum = 1
            """,
            {"ware_id": ware_id},
        )
        return rows[0] if rows else None

    def _camera(self, camera_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_MAP_CAMERA
             where CAMERA_ID = :camera_id
               and ACTIVE = 1
            """,
            {"camera_id": camera_id},
        )
        return rows[0] if rows else None

    def _canvas_code_exists(self, ware_id: int, canvas_code: str) -> bool:
        rows = self.gateway.fetch_all(
            """
            select count(*) CNT
              from RRL_WAREHOUSE_MAP_CANVAS
             where WARE_ID = :ware_id
               and ACTIVE = 1
               and upper(CANVAS_CODE) = upper(:canvas_code)
            """,
            {"ware_id": ware_id, "canvas_code": canvas_code},
        )
        return int(rows[0]["cnt"] or 0) > 0

    def _camera_code_exists(self, canvas_id: int, camera_code: str) -> bool:
        rows = self.gateway.fetch_all(
            """
            select count(*) CNT
              from RRL_WAREHOUSE_MAP_CAMERA
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
               and upper(CAMERA_CODE) = upper(:camera_code)
            """,
            {"canvas_id": canvas_id, "camera_code": camera_code},
        )
        return int(rows[0]["cnt"] or 0) > 0

    def _next_camera_copy_code(self, canvas_id: int, source_code: str) -> str:
        base = f"{source_code}-COPY"
        if len(base) > 72:
            base = base[:72]
        candidate = base
        suffix = 2
        while self._camera_code_exists(canvas_id, candidate):
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def _camera_dependency_counts(self, camera_id: int) -> dict[str, int]:
        rows = self.gateway.fetch_all(
            """
            select 'canvas_objects' KEY, count(*) VALUE
              from RRL_WAREHOUSE_MAP_OBJECT
             where CAMERA_ID = :camera_id
               and ACTIVE = 1
            union all
            select 'passages', count(*)
              from RRL_WAREHOUSE_MAP_PASSAGE
             where CAMERA_ID = :camera_id
               and ACTIVE = 1
            union all
            select 'camera_links', count(*)
              from RRL_WAREHOUSE_MAP_CAMERA_LINK
             where (FROM_CAMERA_ID = :camera_id or TO_CAMERA_ID = :camera_id)
               and ACTIVE = 1
            union all
            select 'topology_cells', count(*)
              from RRL_TOPOLOGY_CELL
             where WAREHOUSE_MAP_CAMERA_ID = :camera_id
               and ACTIVE = 1
            """,
            {"camera_id": camera_id},
        )
        return {str(row["key"]): int(row["value"] or 0) for row in rows}

    def _nextval(self, sequence_name: str) -> int:
        return self.gateway.call_number_plsql(f"begin select {sequence_name}.nextval into :result from dual; end;", {})

    def _canvas(self, canvas_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select c.*,
                   w.NAME WARE_NAME,
                   t.TOPOLOGY_CODE,
                   t.TOPOLOGY_NAME
              from RRL_WAREHOUSE_MAP_CANVAS c
              left join RRL_WARES w
                on w.ID = c.WARE_ID
              left join RRL_WAREHOUSE_TOPOLOGY t
                on t.TOPOLOGY_ID = c.TOPOLOGY_ID
             where c.CANVAS_ID = :canvas_id
               and c.ACTIVE = 1
            """,
            {"canvas_id": canvas_id},
        )
        return rows[0] if rows else None

    def _select_topology(self, ware_id: int, canvas: dict[str, Any] | None) -> dict[str, Any] | None:
        topology_id = canvas.get("topology_id") if canvas else None
        if topology_id is not None:
            rows = self.gateway.fetch_all(
                """
                select t.*, w.NAME WARE_NAME
                  from RRL_WAREHOUSE_TOPOLOGY t
                  left join RRL_WARES w
                    on w.ID = t.WARE_ID
                 where t.TOPOLOGY_ID = :topology_id
                   and t.WARE_ID = :ware_id
                """,
                {"topology_id": topology_id, "ware_id": ware_id},
            )
            return rows[0] if rows else None
        rows = self.gateway.fetch_all(
            """
            select *
              from (
                select t.*, w.NAME WARE_NAME
                  from RRL_WAREHOUSE_TOPOLOGY t
                  left join RRL_WARES w
                    on w.ID = t.WARE_ID
                 where t.WARE_ID = :ware_id
                   and t.STATUS <> 'ARCHIVED'
                 order by case t.STATUS
                            when 'PUBLISHED' then 1
                            when 'VALIDATED' then 2
                            when 'DRAFT' then 3
                            else 9
                          end,
                          t.VERSION_NO desc,
                          t.TOPOLOGY_ID desc
              )
             where rownum = 1
            """,
            {"ware_id": ware_id},
        )
        return rows[0] if rows else None

    def _cameras(self, canvas_id: int | None) -> list[dict[str, Any]]:
        if canvas_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_MAP_CAMERA
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
             order by CAMERA_CODE, CAMERA_ID
            """,
            {"canvas_id": canvas_id},
        )

    def _camera_links(self, canvas_id: int | None) -> list[dict[str, Any]]:
        if canvas_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_MAP_CAMERA_LINK
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
             order by LINK_CODE, CAMERA_LINK_ID
            """,
            {"canvas_id": canvas_id},
        )

    def _canvas_objects(self, canvas_id: int | None) -> list[dict[str, Any]]:
        if canvas_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_MAP_OBJECT
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
             order by CAMERA_ID, OBJECT_KIND, OBJECT_CODE, MAP_OBJECT_ID
            """,
            {"canvas_id": canvas_id},
        )

    def _passages(self, canvas_id: int | None) -> list[dict[str, Any]]:
        if canvas_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select *
              from RRL_WAREHOUSE_MAP_PASSAGE
             where CANVAS_ID = :canvas_id
               and ACTIVE = 1
             order by CAMERA_ID, PASSAGE_CODE, PASSAGE_ID
            """,
            {"canvas_id": canvas_id},
        )

    def _zones(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select *
              from RRL_TOPOLOGY_ZONE
             where TOPOLOGY_ID = :topology_id
               and ACTIVE = 1
             order by ZONE_CODE
            """,
            {"topology_id": topology_id},
        )

    def _aisles(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select *
              from RRL_TOPOLOGY_AISLE
             where TOPOLOGY_ID = :topology_id
               and ACTIVE = 1
             order by AISLE_CODE
            """,
            {"topology_id": topology_id},
        )

    def _gates(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select *
              from RRL_TOPOLOGY_GATE
             where TOPOLOGY_ID = :topology_id
               and ACTIVE = 1
             order by GATE_CODE
            """,
            {"topology_id": topology_id},
        )

    def _topology_cells(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select TOPOLOGY_CELL_ID,
                   TOPOLOGY_ID,
                   WARE_ID,
                   CELL_CODE,
                   LEGACY_CELL_CODE,
                   ZONE_CODE,
                   SECTION_CODE,
                   AISLE_CODE,
                   RACK_CODE,
                   BAY_NO,
                   LEVEL_NO,
                   POSITION_NO,
                   SIDE_CODE,
                   CELL_KIND,
                   STORAGE_AREA_CODE,
                   RESOURCE_AREA_CODE,
                   CELL_SIZE_CODE,
                   MAX_VOLUME_M3,
                   MAX_WEIGHT_KG,
                   X,
                   Y,
                   Z,
                   WIDTH,
                   DEPTH,
                   HEIGHT,
                   ANGLE_DEG,
                   SLOT_LAYER_KIND,
                   WAREHOUSE_MAP_CAMERA_ID,
                   ACTIVE
              from RRL_TOPOLOGY_CELL
             where TOPOLOGY_ID = :topology_id
               and ACTIVE = 1
             order by AISLE_CODE, BAY_NO, SIDE_CODE, LEVEL_NO, CELL_CODE
            """,
            {"topology_id": topology_id},
        )

    def _cell_slots(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select s.CELL_SLOT_ID,
                   s.TOPOLOGY_ID,
                   s.TOPOLOGY_CELL_ID,
                   c.CELL_CODE PARENT_CELL_CODE,
                   c.WAREHOUSE_MAP_CAMERA_ID,
                   s.PARENT_SLOT_LAYER_KIND,
                   s.SLOT_KIND,
                   s.SLOT_CODE,
                   s.SLOT_NAME,
                   s.FRACTION_COUNT,
                   s.FRACTION_INDEX,
                   s.SUB_LEVEL_NO,
                   s.SUB_COLUMN_NO,
                   s.PICK_ORDER,
                   s.STORAGE_ORDER,
                   s.CAPACITY_QTY,
                   s.CAPACITY_VOLUME_M3,
                   s.CAPACITY_WEIGHT_KG,
                   s.X_OFFSET_M,
                   s.Y_OFFSET_M,
                   s.Z_OFFSET_M,
                   s.WIDTH_M,
                   s.DEPTH_M,
                   s.HEIGHT_M,
                   s.CANVAS_OBJECT_ID,
                   s.ACTIVE
              from RRL_TOPOLOGY_CELL_SLOT s
              join RRL_TOPOLOGY_CELL c
                on c.TOPOLOGY_CELL_ID = s.TOPOLOGY_CELL_ID
             where s.TOPOLOGY_ID = :topology_id
               and s.ACTIVE = 1
             order by c.CELL_CODE, s.SLOT_KIND, s.FRACTION_INDEX, s.SLOT_CODE
            """,
            {"topology_id": topology_id},
        )

    def _routes(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select r.PICK_ROUTE_ID,
                   r.TOPOLOGY_ID,
                   r.WARE_ID,
                   r.ROUTE_CODE,
                   r.ROUTE_NAME,
                   r.ROUTE_KIND,
                   r.ROUTE_PATTERN,
                   r.ZONE_CODE,
                   r.START_POINT_CODE,
                   r.END_POINT_CODE,
                   r.STRICT_SEQUENCE,
                   r.STATUS,
                   r.ACTIVE,
                   r.PUBLISHED_AT
              from RRL_PICK_ROUTE r
             where r.TOPOLOGY_ID = :topology_id
               and r.ROUTE_KIND = 'PICK'
               and r.ACTIVE = 1
               and r.STATUS <> 'ARCHIVED'
             order by case r.STATUS
                        when 'PUBLISHED' then 1
                        when 'VALIDATED' then 2
                        when 'DRAFT' then 3
                        else 9
                      end,
                      r.PICK_ROUTE_ID desc
            """,
            {"topology_id": topology_id},
        )

    def _route_rows(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select rc.PICK_ROUTE_CELL_ID,
                   rc.PICK_ROUTE_ID,
                   rc.TOPOLOGY_CELL_ID,
                   rc.CELL_SLOT_ID,
                   s.SLOT_KIND,
                   s.SLOT_CODE,
                   c.WAREHOUSE_MAP_CAMERA_ID,
                   rc.WARE_ID,
                   rc.CELL_CODE,
                   rc.PICK_SEQUENCE,
                   rc.ZONE_CODE,
                   rc.SECTION_CODE,
                   rc.AISLE_CODE,
                   rc.SIDE_CODE,
                   rc.BAY_NO,
                   rc.LEVEL_NO,
                   rc.DIRECTION_CODE,
                   rc.VISIT_GROUP_NO,
                   rc.PATH_SEGMENT_NO,
                   rc.DISTANCE_FROM_PREV_M,
                   rc.TURN_COST_SEC
              from RRL_PICK_ROUTE r
              join RRL_PICK_ROUTE_CELL rc
                on rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID
               and rc.ACTIVE = 1
              left join RRL_TOPOLOGY_CELL_SLOT s
                on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
              left join RRL_TOPOLOGY_CELL c
                on c.TOPOLOGY_CELL_ID = rc.TOPOLOGY_CELL_ID
             where r.TOPOLOGY_ID = :topology_id
               and r.ROUTE_KIND = 'PICK'
               and r.ACTIVE = 1
               and r.STATUS <> 'ARCHIVED'
               and (rc.CELL_SLOT_ID is null or s.SLOT_KIND = 'PICK_FACE_SLOT')
             order by rc.PICK_ROUTE_ID, rc.PICK_SEQUENCE, rc.PICK_ROUTE_CELL_ID
            """,
            {"topology_id": topology_id},
        )

    def _excluded_storage_route_rows(self, topology_id: int | None) -> list[dict[str, Any]]:
        if topology_id is None:
            return []
        return self.gateway.fetch_all(
            """
            select rc.PICK_ROUTE_ID,
                   rc.PICK_ROUTE_CELL_ID,
                   rc.CELL_SLOT_ID,
                   s.SLOT_KIND,
                   s.SLOT_CODE
              from RRL_PICK_ROUTE r
              join RRL_PICK_ROUTE_CELL rc
                on rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID
               and rc.ACTIVE = 1
              join RRL_TOPOLOGY_CELL_SLOT s
                on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
             where r.TOPOLOGY_ID = :topology_id
               and r.ROUTE_KIND = 'PICK'
               and r.ACTIVE = 1
               and r.STATUS <> 'ARCHIVED'
               and s.SLOT_KIND <> 'PICK_FACE_SLOT'
            """,
            {"topology_id": topology_id},
        )


def _decode_json_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_decode_json_row(row) for row in rows]


def _decode_json_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    decoded = dict(row)
    for field in JSON_FIELDS:
        if field in decoded:
            decoded[field] = _json_value(decoded[field])
    return decoded


def _json_value(value: Any) -> Any:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _group_by(rows: list[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    grouped: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row.get(key), []).append(row)
    return grouped


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[Any, int]:
    counts: dict[Any, int] = {}
    for row in rows:
        counts[row.get(key)] = counts.get(row.get(key), 0) + 1
    return counts


def _json_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _clean_code(value: str | None) -> str:
    return (value or "").strip().upper()
