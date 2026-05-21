from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    PickRouteBuildRequest,
    TopologyCellPatchRequest,
    TopologyDistanceRecalculateRequest,
    TopologyGateGenerateRequest,
    WarehouseTopologyCreateRequest,
    WarehouseTopologyGenerateRequest,
)


class WarehouseTopologyService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_topologies(self, ware_id: int | None = None, status: str | None = None) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if ware_id is not None:
            conditions.append("t.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if status:
            conditions.append("upper(t.STATUS) = :status")
            params["status"] = status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select t.TOPOLOGY_ID,
                   t.WARE_ID,
                   w.NAME WARE_NAME,
                   t.TOPOLOGY_CODE,
                   t.TOPOLOGY_NAME,
                   t.VERSION_NO,
                   t.STATUS,
                   t.COMMENT_TEXT,
                   t.CREATED_AT,
                   t.UPDATED_AT,
                   t.PUBLISHED_AT,
                   (select count(*) from RRL_TOPOLOGY_CELL c where c.TOPOLOGY_ID = t.TOPOLOGY_ID and c.ACTIVE = 1) CELL_COUNT,
                   (select count(*) from RRL_TOPOLOGY_AISLE a where a.TOPOLOGY_ID = t.TOPOLOGY_ID and a.ACTIVE = 1) AISLE_COUNT
              from RRL_WAREHOUSE_TOPOLOGY t
              left join RRL_WARES w
                on w.ID = t.WARE_ID
              {where_sql}
             order by t.WARE_ID, t.VERSION_NO desc, t.TOPOLOGY_CODE
            """,
            params,
        )

    def create_topology(self, request: WarehouseTopologyCreateRequest) -> int:
        topology_id = self._nextval("RRL_WH_TOPOLOGY_SQ")
        self.gateway.execute(
            """
            insert into RRL_WAREHOUSE_TOPOLOGY (
              TOPOLOGY_ID, WARE_ID, TOPOLOGY_CODE, TOPOLOGY_NAME,
              VERSION_NO, STATUS, COMMENT_TEXT, CREATED_BY, UPDATED_BY
            ) values (
              :topology_id, :ware_id, upper(:topology_code), :topology_name,
              1, 'DRAFT', :comment_text, substr(:created_by, 1, 50), substr(:created_by, 1, 50)
            )
            """,
            {"topology_id": topology_id, **request.model_dump()},
        )
        self._log_change(topology_id, "TOPOLOGY", topology_id, "CREATE", None, request.model_dump(), request.created_by)
        return topology_id

    def get_topology_map(self, topology_id: int) -> dict[str, Any] | None:
        topology_rows = self.gateway.fetch_all(
            """
            select t.TOPOLOGY_ID, t.WARE_ID, w.NAME WARE_NAME, t.TOPOLOGY_CODE,
                   t.TOPOLOGY_NAME, t.VERSION_NO, t.STATUS, t.COMMENT_TEXT,
                   t.CREATED_AT, t.UPDATED_AT, t.PUBLISHED_AT
              from RRL_WAREHOUSE_TOPOLOGY t
              left join RRL_WARES w on w.ID = t.WARE_ID
             where t.TOPOLOGY_ID = :topology_id
            """,
            {"topology_id": topology_id},
        )
        if not topology_rows:
            return None
        zones = self.gateway.fetch_all(
            """
            select *
              from RRL_TOPOLOGY_ZONE
             where TOPOLOGY_ID = :topology_id
             order by ZONE_CODE
            """,
            {"topology_id": topology_id},
        )
        aisles = self.gateway.fetch_all(
            """
            select *
              from RRL_TOPOLOGY_AISLE
             where TOPOLOGY_ID = :topology_id
             order by AISLE_CODE
            """,
            {"topology_id": topology_id},
        )
        cells = self.gateway.fetch_all(
            """
            select c.*,
                   (
                     select min(d.DISTANCE_M)
                       from RRL_TOPOLOGY_CELL_GATE_DIST d
                      where d.TOPOLOGY_CELL_ID = c.TOPOLOGY_CELL_ID
                        and d.ACTIVE = 1
                        and d.FLOW_KIND in ('OUTBOUND', 'BOTH')
                   ) NEAREST_OUTBOUND_GATE_DISTANCE_M,
                   (
                     select min(d.DISTANCE_M)
                       from RRL_TOPOLOGY_CELL_GATE_DIST d
                      where d.TOPOLOGY_CELL_ID = c.TOPOLOGY_CELL_ID
                        and d.ACTIVE = 1
                        and d.FLOW_KIND in ('INBOUND', 'BOTH')
                   ) NEAREST_INBOUND_GATE_DISTANCE_M
              from RRL_TOPOLOGY_CELL c
             where c.TOPOLOGY_ID = :topology_id
               and c.ACTIVE = 1
             order by c.AISLE_CODE, c.BAY_NO, c.SIDE_CODE, c.LEVEL_NO, c.CELL_CODE
            """,
            {"topology_id": topology_id},
        )
        gates = self.gateway.fetch_all(
            """
            select *
              from RRL_TOPOLOGY_GATE
             where TOPOLOGY_ID = :topology_id
             order by GATE_CODE
            """,
            {"topology_id": topology_id},
        )
        distances = self.gateway.fetch_all(
            """
            select d.CELL_GATE_DISTANCE_ID,
                   d.TOPOLOGY_ID,
                   d.TOPOLOGY_CELL_ID,
                   d.TOPOLOGY_GATE_ID,
                   g.GATE_CODE,
                   g.GATE_KIND,
                   d.FLOW_KIND,
                   d.DISTANCE_M,
                   d.TRAVEL_TIME_SEC,
                   d.ROUTE_KIND,
                   d.CALC_METHOD
              from RRL_TOPOLOGY_CELL_GATE_DIST d
              join RRL_TOPOLOGY_GATE g
                on g.TOPOLOGY_GATE_ID = d.TOPOLOGY_GATE_ID
             where d.TOPOLOGY_ID = :topology_id
               and d.ACTIVE = 1
             order by d.TOPOLOGY_CELL_ID, d.DISTANCE_M, g.GATE_CODE
            """,
            {"topology_id": topology_id},
        )
        routes = self.list_pick_routes(topology_id=topology_id)
        active_route = next((route for route in routes if route.get("active") == 1 and route.get("status") != "ARCHIVED"), None)
        route_cells = self.gateway.fetch_all(
            """
            select rc.*
              from RRL_PICK_ROUTE_CELL rc
             where rc.PICK_ROUTE_ID = :pick_route_id
               and rc.ACTIVE = 1
             order by rc.PICK_ROUTE_ID, rc.PICK_SEQUENCE
            """,
            {"pick_route_id": active_route.get("pick_route_id") if active_route else -1},
        )
        return {
            "topology": topology_rows[0],
            "zones": zones,
            "aisles": aisles,
            "gates": gates,
            "cells": cells,
            "distances": distances,
            "routes": routes,
            "route_cells": route_cells,
        }

    def generate_cells(self, topology_id: int, request: WarehouseTopologyGenerateRequest) -> dict[str, int]:
        topology = self._topology(topology_id)
        if not topology:
            raise HTTPException(status_code=404, detail="Warehouse topology not found.")
        if topology.get("status") == "PUBLISHED":
            raise HTTPException(status_code=409, detail="Published topology cannot be edited; clone it first.")

        if request.overwrite_existing:
            self.gateway.execute(
                """
                update RRL_TOPOLOGY_CELL
                   set ACTIVE = 0, UPDATED_AT = sysdate, UPDATED_BY = substr(:updated_by, 1, 50)
                 where TOPOLOGY_ID = :topology_id
                """,
                {"topology_id": topology_id, "updated_by": request.updated_by},
            )

        self._ensure_zone(topology_id, request)
        created_aisles = 0
        created_cells = 0
        statements: list[tuple[str, dict[str, Any]]] = []
        sides = ["LEFT", "RIGHT"] if int(request.create_both_sides) == 1 else ["LEFT"]
        for aisle_offset in range(request.aisle_count):
            aisle_no = request.start_aisle_no + aisle_offset
            aisle_code = f"{request.aisle_prefix}{aisle_no:02d}"
            x = request.start_x + aisle_offset * request.aisle_spacing_m
            y1 = request.start_y
            y2 = request.start_y + (request.bays_per_aisle - 1) * request.bay_spacing_m
            if not self._aisle_exists(topology_id, aisle_code):
                created_aisles += 1
                statements.append((
                    """
                    insert into RRL_TOPOLOGY_AISLE (
                      TOPOLOGY_AISLE_ID, TOPOLOGY_ID, ZONE_CODE, AISLE_CODE, AISLE_NAME,
                      AISLE_KIND, DIRECTION_CODE, X1, Y1, X2, Y2, WIDTH_M,
                      ALLOW_PICKER, ALLOW_REACHTRUCK, CREATED_BY, UPDATED_BY
                    ) values (
                      RRL_TOPOLOGY_AISLE_SQ.nextval, :topology_id, :zone_code, :aisle_code, :aisle_name,
                      'PICK_AISLE', 'BOTH', :x1, :y1, :x2, :y2, :width_m,
                      1, 1, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                    )
                    """,
                    {
                        "topology_id": topology_id,
                        "zone_code": request.zone_code,
                        "aisle_code": aisle_code,
                        "aisle_name": f"Аллея {aisle_code}",
                        "x1": x,
                        "y1": y1,
                        "x2": x,
                        "y2": y2,
                        "width_m": request.aisle_spacing_m,
                        "updated_by": request.updated_by,
                    },
                ))
            for bay in range(1, request.bays_per_aisle + 1):
                for level in range(1, request.levels + 1):
                    for side in sides:
                        side_code = side.upper()
                        cell_code = f"{aisle_code}-B{bay:03d}-L{level}-{side_code[0]}"
                        if self._cell_exists(topology_id, cell_code):
                            continue
                        created_cells += 1
                        side_shift = -request.pick_face_depth_m if side_code == "LEFT" else request.pick_face_depth_m
                        statements.append((
                            """
                            insert into RRL_TOPOLOGY_CELL (
                              TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE, LEGACY_CELL_CODE,
                              ZONE_CODE, SECTION_CODE, AISLE_CODE, BAY_NO, LEVEL_NO, POSITION_NO,
                              SIDE_CODE, CELL_KIND, MAX_VOLUME_M3, MAX_WEIGHT_KG,
                              X, Y, Z, WIDTH, DEPTH, HEIGHT, ANGLE_DEG, CREATED_BY, UPDATED_BY
                            ) values (
                              RRL_TOPOLOGY_CELL_SQ.nextval, :topology_id, :ware_id, :cell_code, :cell_code,
                              :zone_code, :section_code, :aisle_code, :bay_no, :level_no, :position_no,
                              :side_code, :cell_kind, :max_volume_m3, :max_weight_kg,
                              :x, :y, :z, :width, :depth, :height, 0, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                            )
                            """,
                            {
                                "topology_id": topology_id,
                                "ware_id": topology["ware_id"],
                                "cell_code": cell_code,
                                "zone_code": request.zone_code,
                                "section_code": request.section_code,
                                "aisle_code": aisle_code,
                                "bay_no": bay,
                                "level_no": level,
                                "position_no": bay,
                                "side_code": side_code,
                                "cell_kind": request.cell_kind,
                                "max_volume_m3": request.max_volume_m3,
                                "max_weight_kg": request.max_weight_kg,
                                "x": x + side_shift,
                                "y": request.start_y + (bay - 1) * request.bay_spacing_m,
                                "z": (level - 1) * request.cell_height_m,
                                "width": request.cell_width_m,
                                "depth": request.pick_face_depth_m,
                                "height": request.cell_height_m,
                                "updated_by": request.updated_by,
                            },
                        ))
        if statements:
            self.gateway.execute_many(statements)
        self._log_change(topology_id, "CELL", None, "GENERATE", None, request.model_dump(), request.updated_by)
        return {"topology_id": topology_id, "created_aisles": created_aisles, "created_cells": created_cells}

    def generate_gates(self, topology_id: int, request: TopologyGateGenerateRequest) -> dict[str, int]:
        topology = self._topology(topology_id)
        if not topology:
            raise HTTPException(status_code=404, detail="Warehouse topology not found.")
        if topology.get("status") == "PUBLISHED":
            raise HTTPException(status_code=409, detail="Published topology cannot be edited; clone it first.")
        if request.overwrite_existing:
            self.gateway.execute(
                """
                update RRL_TOPOLOGY_GATE
                   set ACTIVE = 0, UPDATED_AT = sysdate, UPDATED_BY = substr(:updated_by, 1, 50)
                 where TOPOLOGY_ID = :topology_id
                """,
                {"topology_id": topology_id, "updated_by": request.updated_by},
            )
        statements: list[tuple[str, dict[str, Any]]] = []
        created_gates = 0
        for index in range(1, request.gate_count + 1):
            gate_code = f"{request.gate_prefix}{index:02d}"
            exists = self.gateway.fetch_all(
                """
                select 1
                  from RRL_TOPOLOGY_GATE
                 where TOPOLOGY_ID = :topology_id
                   and GATE_CODE = :gate_code
                   and ACTIVE = 1
                """,
                {"topology_id": topology_id, "gate_code": gate_code},
            )
            if exists:
                continue
            created_gates += 1
            statements.append((
                """
                insert into RRL_TOPOLOGY_GATE (
                  TOPOLOGY_GATE_ID, TOPOLOGY_ID, WARE_ID, GATE_CODE, GATE_NAME,
                  GATE_KIND, STAGING_ZONE_CODE, VEHICLE_CLASS, X, Y, CREATED_BY, UPDATED_BY
                ) values (
                  RRL_TOPOLOGY_GATE_SQ.nextval, :topology_id, :ware_id, :gate_code, :gate_name,
                  upper(:gate_kind), :staging_zone_code, :vehicle_class, :x, :y,
                  substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                )
                """,
                {
                    "topology_id": topology_id,
                    "ware_id": topology["ware_id"],
                    "gate_code": gate_code,
                    "gate_name": f"Ворота {gate_code}",
                    "gate_kind": request.gate_kind,
                    "staging_zone_code": request.staging_zone_code,
                    "vehicle_class": request.vehicle_class,
                    "x": request.start_x + (index - 1) * request.spacing_m,
                    "y": request.start_y,
                    "updated_by": request.updated_by,
                },
            ))
        if statements:
            self.gateway.execute_many(statements)
        self._log_change(topology_id, "GATE", None, "GENERATE", None, request.model_dump(), request.updated_by)
        return {"topology_id": topology_id, "created_gates": created_gates}

    def recalculate_gate_distances(
        self,
        topology_id: int,
        request: TopologyDistanceRecalculateRequest,
    ) -> dict[str, int]:
        topology = self._topology(topology_id)
        if not topology:
            raise HTTPException(status_code=404, detail="Warehouse topology not found.")
        cells = self.gateway.fetch_all(
            """
            select TOPOLOGY_CELL_ID, CELL_CODE, CELL_KIND, X, Y
              from RRL_TOPOLOGY_CELL
             where TOPOLOGY_ID = :topology_id
               and ACTIVE = 1
               and CELL_KIND in ('PICK_FACE', 'DYNAMIC_PICK_FACE', 'STORAGE')
            """,
            {"topology_id": topology_id},
        )
        gates = self.gateway.fetch_all(
            """
            select TOPOLOGY_GATE_ID, GATE_CODE, GATE_KIND, X, Y
              from RRL_TOPOLOGY_GATE
             where TOPOLOGY_ID = :topology_id
               and ACTIVE = 1
            """,
            {"topology_id": topology_id},
        )
        if not cells or not gates:
            raise HTTPException(status_code=409, detail="Topology must contain active cells and gates before distance calculation.")
        self.gateway.execute(
            """
            update RRL_TOPOLOGY_CELL_GATE_DIST
               set ACTIVE = 0,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:updated_by, 1, 50)
             where TOPOLOGY_ID = :topology_id
               and FLOW_KIND = upper(:flow_kind)
            """,
            {"topology_id": topology_id, "flow_kind": request.flow_kind, "updated_by": request.updated_by},
        )
        statements: list[tuple[str, dict[str, Any]]] = []
        flow_kind = request.flow_kind.upper()
        for cell in cells:
            speed = request.reachtruck_speed_mps if cell.get("cell_kind") == "STORAGE" and request.use_reachtruck_for_storage else request.picker_speed_mps
            for gate in gates:
                distance_m = self._gate_distance(cell, gate)
                statements.append((
                    """
                    merge into RRL_TOPOLOGY_CELL_GATE_DIST d
                    using (
                      select :topology_id TOPOLOGY_ID,
                             :topology_cell_id TOPOLOGY_CELL_ID,
                             :topology_gate_id TOPOLOGY_GATE_ID,
                             :flow_kind FLOW_KIND,
                             :distance_m DISTANCE_M,
                             :travel_time_sec TRAVEL_TIME_SEC,
                             substr(:updated_by, 1, 50) UPDATED_BY
                        from dual
                    ) s
                       on (d.TOPOLOGY_CELL_ID = s.TOPOLOGY_CELL_ID
                       and d.TOPOLOGY_GATE_ID = s.TOPOLOGY_GATE_ID
                       and d.FLOW_KIND = s.FLOW_KIND)
                     when matched then update
                       set d.TOPOLOGY_ID = s.TOPOLOGY_ID,
                           d.DISTANCE_M = s.DISTANCE_M,
                           d.TRAVEL_TIME_SEC = s.TRAVEL_TIME_SEC,
                           d.ROUTE_KIND = 'TOPOLOGY_ESTIMATE',
                           d.CALC_METHOD = 'MANHATTAN',
                           d.ACTIVE = 1,
                           d.UPDATED_AT = sysdate,
                           d.UPDATED_BY = s.UPDATED_BY
                     when not matched then insert (
                       CELL_GATE_DISTANCE_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, TOPOLOGY_GATE_ID,
                       FLOW_KIND, DISTANCE_M, TRAVEL_TIME_SEC, ROUTE_KIND, CALC_METHOD,
                       ACTIVE, CREATED_BY, UPDATED_BY
                     ) values (
                       RRL_TOPO_CELL_GATE_DIST_SQ.nextval, s.TOPOLOGY_ID, s.TOPOLOGY_CELL_ID, s.TOPOLOGY_GATE_ID,
                       s.FLOW_KIND, s.DISTANCE_M, s.TRAVEL_TIME_SEC, 'TOPOLOGY_ESTIMATE', 'MANHATTAN',
                       1, s.UPDATED_BY, s.UPDATED_BY
                     )
                    """,
                    {
                        "topology_id": topology_id,
                        "topology_cell_id": cell["topology_cell_id"],
                        "topology_gate_id": gate["topology_gate_id"],
                        "flow_kind": flow_kind,
                        "distance_m": distance_m,
                        "travel_time_sec": round(distance_m / speed, 1),
                        "updated_by": request.updated_by,
                    },
                ))
        if statements:
            self.gateway.execute_many(statements)
        self._log_change(topology_id, "DISTANCE", None, "RECALCULATE", None, request.model_dump(), request.updated_by)
        return {"topology_id": topology_id, "distance_count": len(statements)}

    def patch_cell(self, topology_cell_id: int, request: TopologyCellPatchRequest) -> None:
        rows = self.gateway.fetch_all(
            "select TOPOLOGY_ID, ACTIVE from RRL_TOPOLOGY_CELL where TOPOLOGY_CELL_ID = :id",
            {"id": topology_cell_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Topology cell not found.")
        updates: list[str] = ["UPDATED_AT = sysdate", "UPDATED_BY = substr(:updated_by, 1, 50)"]
        params: dict[str, Any] = {"topology_cell_id": topology_cell_id, "updated_by": request.updated_by}
        for field, column in (
            ("x", "X"),
            ("y", "Y"),
            ("z", "Z"),
            ("zone_code", "ZONE_CODE"),
            ("section_code", "SECTION_CODE"),
            ("aisle_code", "AISLE_CODE"),
            ("side_code", "SIDE_CODE"),
            ("cell_kind", "CELL_KIND"),
            ("active", "ACTIVE"),
        ):
            value = getattr(request, field)
            if value is not None:
                updates.append(f"{column} = :{field}")
                params[field] = value.upper() if isinstance(value, str) and field.endswith("_code") else value
        self.gateway.execute(
            f"""
            update RRL_TOPOLOGY_CELL
               set {", ".join(updates)}
             where TOPOLOGY_CELL_ID = :topology_cell_id
            """,
            params,
        )
        self._log_change(rows[0]["topology_id"], "CELL", topology_cell_id, "PATCH", None, request.model_dump(), request.updated_by)

    def validate_topology(self, topology_id: int) -> dict[str, Any]:
        checks = {
            "duplicate_cells": self.gateway.fetch_all(
                """
                select CELL_CODE, count(*) CNT
                  from RRL_TOPOLOGY_CELL
                 where TOPOLOGY_ID = :topology_id
                   and ACTIVE = 1
                 group by CELL_CODE
                having count(*) > 1
                """,
                {"topology_id": topology_id},
            ),
            "pick_faces_without_aisle": self.gateway.fetch_all(
                """
                select CELL_CODE
                  from RRL_TOPOLOGY_CELL
                 where TOPOLOGY_ID = :topology_id
                   and ACTIVE = 1
                   and CELL_KIND in ('PICK_FACE', 'DYNAMIC_PICK_FACE')
                   and AISLE_CODE is null
                """,
                {"topology_id": topology_id},
            ),
            "pick_faces_without_side": self.gateway.fetch_all(
                """
                select CELL_CODE
                  from RRL_TOPOLOGY_CELL
                 where TOPOLOGY_ID = :topology_id
                   and ACTIVE = 1
                   and CELL_KIND in ('PICK_FACE', 'DYNAMIC_PICK_FACE')
                   and SIDE_CODE not in ('LEFT', 'RIGHT')
                """,
                {"topology_id": topology_id},
            ),
            "multiple_active_pick_routes": self.gateway.fetch_all(
                """
                select TOPOLOGY_ID, count(*) CNT
                  from RRL_PICK_ROUTE
                 where TOPOLOGY_ID = :topology_id
                   and ROUTE_KIND = 'PICK'
                   and ACTIVE = 1
                   and STATUS <> 'ARCHIVED'
                 group by TOPOLOGY_ID
                having count(*) > 1
                """,
                {"topology_id": topology_id},
            ),
            "duplicate_route_sequence": self.gateway.fetch_all(
                """
                select r.PICK_ROUTE_ID, rc.PICK_SEQUENCE, count(*) CNT
                  from RRL_PICK_ROUTE r
                  join RRL_PICK_ROUTE_CELL rc
                    on rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID
                 where r.TOPOLOGY_ID = :topology_id
                   and r.ACTIVE = 1
                   and r.STATUS <> 'ARCHIVED'
                   and rc.ACTIVE = 1
                 group by r.PICK_ROUTE_ID, rc.PICK_SEQUENCE
                having count(*) > 1
                """,
                {"topology_id": topology_id},
            ),
            "duplicate_route_cell": self.gateway.fetch_all(
                """
                select r.PICK_ROUTE_ID, rc.TOPOLOGY_CELL_ID, count(*) CNT
                  from RRL_PICK_ROUTE r
                  join RRL_PICK_ROUTE_CELL rc
                    on rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID
                 where r.TOPOLOGY_ID = :topology_id
                   and r.ACTIVE = 1
                   and r.STATUS <> 'ARCHIVED'
                   and rc.ACTIVE = 1
                   and rc.TOPOLOGY_CELL_ID is not null
                 group by r.PICK_ROUTE_ID, rc.TOPOLOGY_CELL_ID
                having count(*) > 1
                """,
                {"topology_id": topology_id},
            ),
            "pick_faces_on_inactive_route": self.gateway.fetch_all(
                """
                select pf.PICK_FACE_ID,
                       pf.CELL_CODE,
                       pf.PICK_ROUTE_CELL_ID,
                       rc.PICK_ROUTE_ID,
                       r.STATUS,
                       r.ACTIVE
                  from RRL_PICK_FACE pf
                  join RRL_PICK_ROUTE_CELL rc
                    on rc.PICK_ROUTE_CELL_ID = pf.PICK_ROUTE_CELL_ID
                  join RRL_PICK_ROUTE r
                    on r.PICK_ROUTE_ID = rc.PICK_ROUTE_ID
                 where pf.ACTIVE = 1
                   and r.TOPOLOGY_ID = :topology_id
                   and (r.ACTIVE <> 1 or r.STATUS = 'ARCHIVED' or rc.ACTIVE <> 1)
                """,
                {"topology_id": topology_id},
            ),
        }
        error_count = sum(len(value) for value in checks.values())
        if error_count == 0:
            self.gateway.execute(
                """
                update RRL_WAREHOUSE_TOPOLOGY
                   set STATUS = case when STATUS = 'DRAFT' then 'VALIDATED' else STATUS end,
                       UPDATED_AT = sysdate
                 where TOPOLOGY_ID = :topology_id
                """,
                {"topology_id": topology_id},
            )
        return {"topology_id": topology_id, "valid": error_count == 0, "error_count": error_count, "checks": checks}

    def publish_topology(self, topology_id: int, user: str) -> None:
        topology = self._topology(topology_id)
        if not topology:
            raise HTTPException(status_code=404, detail="Warehouse topology not found.")
        validation = self.validate_topology(topology_id)
        if not validation["valid"]:
            raise HTTPException(status_code=409, detail={"message": "Topology has validation errors.", "validation": validation})
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TOPOLOGY
               set STATUS = 'ARCHIVED',
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:user, 1, 50)
             where WARE_ID = :ware_id
               and TOPOLOGY_ID <> :topology_id
               and STATUS = 'PUBLISHED'
            """,
            {"ware_id": topology["ware_id"], "topology_id": topology_id, "user": user},
        )
        self.gateway.execute(
            """
            update RRL_WAREHOUSE_TOPOLOGY
               set STATUS = 'PUBLISHED',
                   PUBLISHED_AT = sysdate,
                   PUBLISHED_BY = substr(:user, 1, 50),
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:user, 1, 50)
             where TOPOLOGY_ID = :topology_id
            """,
            {"topology_id": topology_id, "user": user},
        )
        self._log_change(topology_id, "TOPOLOGY", topology_id, "PUBLISH", None, {"status": "PUBLISHED"}, user)

    def list_pick_routes(
        self,
        topology_id: int | None = None,
        ware_id: int | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {}
        if topology_id is not None:
            conditions.append("r.TOPOLOGY_ID = :topology_id")
            params["topology_id"] = topology_id
        if ware_id is not None:
            conditions.append("r.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if status:
            conditions.append("upper(r.STATUS) = :status")
            params["status"] = status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select r.PICK_ROUTE_ID, r.TOPOLOGY_ID, r.WARE_ID, w.NAME WARE_NAME,
                   r.ROUTE_CODE, r.ROUTE_NAME, r.ROUTE_KIND, r.ROUTE_PATTERN,
                   r.ZONE_CODE, r.START_POINT_CODE, r.END_POINT_CODE,
                   r.STRICT_SEQUENCE, r.STATUS, r.ACTIVE, r.PUBLISHED_AT,
                   count(rc.PICK_ROUTE_CELL_ID) CELL_COUNT
              from RRL_PICK_ROUTE r
              left join RRL_WARES w on w.ID = r.WARE_ID
              left join RRL_PICK_ROUTE_CELL rc on rc.PICK_ROUTE_ID = r.PICK_ROUTE_ID and rc.ACTIVE = 1
              {where_sql}
             group by r.PICK_ROUTE_ID, r.TOPOLOGY_ID, r.WARE_ID, w.NAME,
                      r.ROUTE_CODE, r.ROUTE_NAME, r.ROUTE_KIND, r.ROUTE_PATTERN,
                      r.ZONE_CODE, r.START_POINT_CODE, r.END_POINT_CODE,
                      r.STRICT_SEQUENCE, r.STATUS, r.ACTIVE, r.PUBLISHED_AT
             order by r.WARE_ID, r.ROUTE_CODE, r.ACTIVE desc,
                      case r.STATUS when 'PUBLISHED' then 1 when 'DRAFT' then 2 when 'VALIDATED' then 3 else 9 end,
                      r.PICK_ROUTE_ID desc
            """,
            params,
        )

    def build_pick_route(self, request: PickRouteBuildRequest) -> dict[str, int]:
        topology = self._topology(request.topology_id)
        if not topology:
            raise HTTPException(status_code=404, detail="Warehouse topology not found.")
        pick_route_id = request.pick_route_id
        if not pick_route_id:
            existing_for_topology = self.gateway.fetch_all(
                """
                select PICK_ROUTE_ID
                  from RRL_PICK_ROUTE
                 where TOPOLOGY_ID = :topology_id
                   and WARE_ID = :ware_id
                   and ROUTE_KIND = 'PICK'
                   and ACTIVE = 1
                   and STATUS <> 'ARCHIVED'
                 order by case STATUS when 'PUBLISHED' then 1 when 'VALIDATED' then 2 when 'DRAFT' then 3 else 9 end,
                          PICK_ROUTE_ID desc
                """,
                {
                    "topology_id": request.topology_id,
                    "ware_id": request.ware_id,
                },
            )
            pick_route_id = existing_for_topology[0]["pick_route_id"] if existing_for_topology else self._nextval("RRL_PICK_ROUTE_SQ")
        existing = self.gateway.fetch_all(
            "select PICK_ROUTE_ID from RRL_PICK_ROUTE where PICK_ROUTE_ID = :pick_route_id",
            {"pick_route_id": pick_route_id},
        )
        route_params = {
            "pick_route_id": pick_route_id,
            "topology_id": request.topology_id,
            "route_code": request.route_code,
            "route_name": request.route_name,
            "ware_id": request.ware_id,
            "route_pattern": request.route_pattern,
            "zone_code": request.zone_code,
            "strict_sequence": request.strict_sequence,
            "updated_by": request.updated_by,
        }
        if existing:
            self.gateway.execute(
                """
                update RRL_PICK_ROUTE
                   set TOPOLOGY_ID = :topology_id,
                       ROUTE_CODE = upper(:route_code),
                       ROUTE_NAME = :route_name,
                       WARE_ID = :ware_id,
                       ROUTE_KIND = 'PICK',
                       ROUTE_PATTERN = upper(:route_pattern),
                       ZONE_CODE = :zone_code,
                       STRICT_SEQUENCE = :strict_sequence,
                       STATUS = 'DRAFT',
                       ACTIVE = 1,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where PICK_ROUTE_ID = :pick_route_id
                """,
                route_params,
            )
            self._archive_other_pick_routes(request.topology_id, pick_route_id, request.updated_by)
            self.gateway.execute(
                """
                update RRL_PICK_ROUTE_CELL
                   set ACTIVE = 0,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:updated_by, 1, 50)
                 where PICK_ROUTE_ID = :pick_route_id
                """,
                {"pick_route_id": pick_route_id, "updated_by": request.updated_by},
            )
        else:
            self._archive_other_pick_routes(request.topology_id, pick_route_id, request.updated_by)
            self.gateway.execute(
                """
                insert into RRL_PICK_ROUTE (
                  PICK_ROUTE_ID, TOPOLOGY_ID, ROUTE_CODE, ROUTE_NAME, WARE_ID,
                  ROUTE_KIND, ROUTE_PATTERN, ZONE_CODE, STRICT_SEQUENCE,
                  STATUS, ACTIVE, CREATED_BY, UPDATED_BY
                ) values (
                  :pick_route_id, :topology_id, upper(:route_code), :route_name, :ware_id,
                  'PICK', upper(:route_pattern), :zone_code, :strict_sequence,
                  'DRAFT', 1, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                )
                """,
                route_params,
            )

        cells = self._route_source_cells(request)
        if not cells and request.cell_ids:
            request.cell_ids = None
            cells = self._route_source_cells(request)
        if not cells and request.aisle_codes:
            request.aisle_codes = None
            cells = self._route_source_cells(request)
        if not cells:
            raise HTTPException(status_code=409, detail="No active pick-face cells found for selected topology area.")
        cells = self._order_route_cells(cells, request)
        statements: list[tuple[str, dict[str, Any]]] = []
        for index, cell in enumerate(cells, start=1):
            prev = cells[index - 2] if index > 1 else None
            distance = self._distance(prev, cell) if prev else 0
            statements.append((
                """
                insert into RRL_PICK_ROUTE_CELL (
                  PICK_ROUTE_CELL_ID, PICK_ROUTE_ID, TOPOLOGY_CELL_ID, WARE_ID, CELL_CODE,
                  PICK_SEQUENCE, ZONE_CODE, SECTION_CODE, AISLE_CODE, SIDE_CODE,
                  BAY_NO, LEVEL_NO, DIRECTION_CODE, VISIT_GROUP_NO, PATH_SEGMENT_NO,
                  DISTANCE_FROM_PREV_M, TURN_COST_SEC, ACTIVE, CREATED_BY, UPDATED_BY
                ) values (
                  RRL_PICK_ROUTE_CELL_SQ.nextval, :pick_route_id, :topology_cell_id, :ware_id, :cell_code,
                  :pick_sequence, :zone_code, :section_code, :aisle_code, :side_code,
                  :bay_no, :level_no, :direction_code, :visit_group_no, :path_segment_no,
                  :distance_from_prev_m, :turn_cost_sec, 1, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
                )
                """,
                {
                    "pick_route_id": pick_route_id,
                    "topology_cell_id": cell.get("topology_cell_id"),
                    "ware_id": cell.get("ware_id"),
                    "cell_code": cell.get("cell_code"),
                    "pick_sequence": index,
                    "zone_code": cell.get("zone_code"),
                    "section_code": cell.get("section_code"),
                    "aisle_code": cell.get("aisle_code"),
                    "side_code": cell.get("side_code"),
                    "bay_no": cell.get("bay_no"),
                    "level_no": cell.get("level_no"),
                    "direction_code": "FORWARD",
                    "visit_group_no": 1,
                    "path_segment_no": index,
                    "distance_from_prev_m": distance,
                    "turn_cost_sec": 0 if not prev or prev.get("aisle_code") == cell.get("aisle_code") else 20,
                    "updated_by": request.updated_by,
                },
            ))
        if statements:
            self.gateway.execute_many(statements)
        self._assert_linear_route_invariants(pick_route_id)
        self._log_change(request.topology_id, "PICK_ROUTE", pick_route_id, "BUILD", None, request.model_dump(), request.updated_by)
        return {"pick_route_id": pick_route_id, "route_cell_count": len(cells)}

    def publish_pick_route(self, pick_route_id: int, user: str) -> None:
        rows = self.gateway.fetch_all(
            "select TOPOLOGY_ID, WARE_ID from RRL_PICK_ROUTE where PICK_ROUTE_ID = :pick_route_id",
            {"pick_route_id": pick_route_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Pick route not found.")
        route = rows[0]
        cell_count = self.gateway.fetch_all(
            """
            select count(*) CNT
              from RRL_PICK_ROUTE_CELL
             where PICK_ROUTE_ID = :pick_route_id
               and ACTIVE = 1
            """,
            {"pick_route_id": pick_route_id},
        )[0]["cnt"]
        if int(cell_count or 0) == 0:
            raise HTTPException(status_code=409, detail="Pick route has no active cells.")
        self.gateway.execute(
            """
            update RRL_PICK_ROUTE
               set STATUS = 'ARCHIVED',
                   ACTIVE = 0,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:user, 1, 50)
             where TOPOLOGY_ID = :topology_id
               and PICK_ROUTE_ID <> :pick_route_id
               and ROUTE_KIND = 'PICK'
               and STATUS = 'PUBLISHED'
            """,
            {"topology_id": route.get("topology_id"), "pick_route_id": pick_route_id, "user": user},
        )
        self.gateway.execute(
            """
            update RRL_PICK_ROUTE
               set STATUS = 'PUBLISHED',
                   ACTIVE = 1,
                   PUBLISHED_AT = sysdate,
                   PUBLISHED_BY = substr(:user, 1, 50),
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:user, 1, 50)
             where PICK_ROUTE_ID = :pick_route_id
            """,
            {"pick_route_id": pick_route_id, "user": user},
        )
        self._log_change(route.get("topology_id"), "PICK_ROUTE", pick_route_id, "PUBLISH", None, {"status": "PUBLISHED"}, user)

    def _route_source_cells(self, request: PickRouteBuildRequest) -> list[dict[str, Any]]:
        conditions = [
            "TOPOLOGY_ID = :topology_id",
            "ACTIVE = 1",
            "CELL_KIND in ('PICK_FACE', 'DYNAMIC_PICK_FACE')",
        ]
        params: dict[str, Any] = {"topology_id": request.topology_id}
        if request.zone_code:
            conditions.append("ZONE_CODE = :zone_code")
            params["zone_code"] = request.zone_code
        if request.aisle_codes:
            placeholders = []
            for index, aisle_code in enumerate(request.aisle_codes):
                key = f"aisle_{index}"
                placeholders.append(f":{key}")
                params[key] = aisle_code
            conditions.append(f"AISLE_CODE in ({', '.join(placeholders)})")
        if request.cell_ids:
            placeholders = []
            for index, cell_id in enumerate(request.cell_ids):
                key = f"cell_{index}"
                placeholders.append(f":{key}")
                params[key] = cell_id
            conditions.append(f"TOPOLOGY_CELL_ID in ({', '.join(placeholders)})")
        return self.gateway.fetch_all(
            f"""
            select TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE, ZONE_CODE,
                   SECTION_CODE, AISLE_CODE, BAY_NO, LEVEL_NO, SIDE_CODE, X, Y, Z
              from RRL_TOPOLOGY_CELL
             where {" and ".join(conditions)}
            """,
            params,
        )

    def _order_route_cells(self, cells: list[dict[str, Any]], request: PickRouteBuildRequest) -> list[dict[str, Any]]:
        pattern = (request.route_pattern or "Z").upper()
        side_rank = {side.upper(): index for index, side in enumerate(request.side_order or ["LEFT", "RIGHT"])}
        aisle_order = {code: index for index, code in enumerate(request.aisle_codes or [])}
        groups: dict[str, list[dict[str, Any]]] = {}
        for cell in cells:
            groups.setdefault(str(cell.get("aisle_code") or ""), []).append(cell)

        ordered: list[dict[str, Any]] = []
        sorted_groups = sorted(groups.items(), key=lambda item: (aisle_order.get(item[0], 999), item[0]))
        for index, (_aisle_code, aisle_cells) in enumerate(sorted_groups):
            if pattern == "U_SHAPE":
                ordered.extend(self._order_aisle_as_u_shape(aisle_cells, side_rank))
                continue
            reverse = pattern in {"Z", "SNAKE"} and index % 2 == 1
            side_first = pattern == "LINEAR"
            aisle_cells.sort(key=lambda row: (
                side_rank.get(str(row.get("side_code") or "").upper(), 99) if side_first else 0,
                -float(row.get("bay_no") or 0) if reverse else float(row.get("bay_no") or 0),
                0 if side_first else side_rank.get(str(row.get("side_code") or "").upper(), 99),
                float(row.get("level_no") or 0),
            ))
            ordered.extend(aisle_cells)
        return ordered

    def _order_aisle_as_u_shape(self, cells: list[dict[str, Any]], side_rank: dict[str, int]) -> list[dict[str, Any]]:
        def by_bay_asc(row: dict[str, Any]) -> tuple[float, float, int]:
            return (
                float(row.get("bay_no") or 0),
                float(row.get("level_no") or 0),
                side_rank.get(str(row.get("side_code") or "").upper(), 99),
            )

        def by_bay_desc(row: dict[str, Any]) -> tuple[float, float, int]:
            return (
                -float(row.get("bay_no") or 0),
                float(row.get("level_no") or 0),
                side_rank.get(str(row.get("side_code") or "").upper(), 99),
            )

        left = [row for row in cells if str(row.get("side_code") or "").upper() == "LEFT"]
        right = [row for row in cells if str(row.get("side_code") or "").upper() == "RIGHT"]
        center = [row for row in cells if str(row.get("side_code") or "").upper() not in {"LEFT", "RIGHT"}]
        return sorted(left, key=by_bay_asc) + sorted(right, key=by_bay_desc) + sorted(center, key=by_bay_asc)

    def _ensure_zone(self, topology_id: int, request: WarehouseTopologyGenerateRequest) -> None:
        exists = self.gateway.fetch_all(
            "select TOPOLOGY_ZONE_ID from RRL_TOPOLOGY_ZONE where TOPOLOGY_ID = :topology_id and ZONE_CODE = :zone_code",
            {"topology_id": topology_id, "zone_code": request.zone_code},
        )
        if exists:
            return
        self.gateway.execute(
            """
            insert into RRL_TOPOLOGY_ZONE (
              TOPOLOGY_ZONE_ID, TOPOLOGY_ID, ZONE_CODE, ZONE_NAME, ZONE_KIND,
              X, Y, WIDTH, HEIGHT, CREATED_BY, UPDATED_BY
            ) values (
              RRL_TOPOLOGY_ZONE_SQ.nextval, :topology_id, :zone_code, :zone_name, 'PICKING',
              :x, :y, :width, :height, substr(:updated_by, 1, 50), substr(:updated_by, 1, 50)
            )
            """,
            {
                "topology_id": topology_id,
                "zone_code": request.zone_code,
                "zone_name": request.zone_name,
                "x": request.start_x - request.aisle_spacing_m,
                "y": request.start_y - request.bay_spacing_m,
                "width": request.aisle_count * request.aisle_spacing_m + request.aisle_spacing_m,
                "height": request.bays_per_aisle * request.bay_spacing_m + request.bay_spacing_m,
                "updated_by": request.updated_by,
            },
        )

    def _topology(self, topology_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            "select * from RRL_WAREHOUSE_TOPOLOGY where TOPOLOGY_ID = :topology_id",
            {"topology_id": topology_id},
        )
        return rows[0] if rows else None

    def _archive_other_pick_routes(self, topology_id: int, keep_route_id: int, user: str | None) -> None:
        self.gateway.execute(
            """
            update RRL_PICK_ROUTE
               set STATUS = 'ARCHIVED',
                   ACTIVE = 0,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = substr(:user_id, 1, 50)
             where TOPOLOGY_ID = :topology_id
               and ROUTE_KIND = 'PICK'
               and PICK_ROUTE_ID <> :keep_route_id
               and ACTIVE = 1
            """,
            {"topology_id": topology_id, "keep_route_id": keep_route_id, "user_id": user},
        )

    def _assert_linear_route_invariants(self, pick_route_id: int) -> None:
        checks = self.gateway.fetch_all(
            """
            select 'DUP_SEQUENCE' CHECK_KIND, count(*) CNT
              from (
                select PICK_SEQUENCE
                  from RRL_PICK_ROUTE_CELL
                 where PICK_ROUTE_ID = :pick_route_id
                   and ACTIVE = 1
                 group by PICK_SEQUENCE
                having count(*) > 1
              )
            union all
            select 'DUP_CELL' CHECK_KIND, count(*) CNT
              from (
                select TOPOLOGY_CELL_ID
                  from RRL_PICK_ROUTE_CELL
                 where PICK_ROUTE_ID = :pick_route_id
                   and ACTIVE = 1
                   and TOPOLOGY_CELL_ID is not null
                 group by TOPOLOGY_CELL_ID
                having count(*) > 1
              )
            """,
            {"pick_route_id": pick_route_id},
        )
        failed = [row for row in checks if int(row.get("cnt") or 0) > 0]
        if failed:
            raise HTTPException(status_code=409, detail={"message": "Pick route violates linear order invariants.", "checks": failed})

    def _aisle_exists(self, topology_id: int, aisle_code: str) -> bool:
        return bool(self.gateway.fetch_all(
            "select 1 from RRL_TOPOLOGY_AISLE where TOPOLOGY_ID = :topology_id and AISLE_CODE = :aisle_code",
            {"topology_id": topology_id, "aisle_code": aisle_code},
        ))

    def _cell_exists(self, topology_id: int, cell_code: str) -> bool:
        return bool(self.gateway.fetch_all(
            "select 1 from RRL_TOPOLOGY_CELL where TOPOLOGY_ID = :topology_id and CELL_CODE = :cell_code and ACTIVE = 1",
            {"topology_id": topology_id, "cell_code": cell_code},
        ))

    def _nextval(self, sequence_name: str) -> int:
        return self.gateway.call_number_plsql(f"begin select {sequence_name}.nextval into :result from dual; end;", {})

    def _log_change(
        self,
        topology_id: int | None,
        entity_kind: str,
        entity_id: int | None,
        change_kind: str,
        old_value: Any,
        new_value: Any,
        user: str | None,
    ) -> None:
        if topology_id is None:
            return
        self.gateway.execute(
            """
            insert into RRL_TOPOLOGY_CHANGE_LOG (
              CHANGE_ID, TOPOLOGY_ID, ENTITY_KIND, ENTITY_ID, CHANGE_KIND,
              OLD_VALUE_JSON, NEW_VALUE_JSON, CREATED_BY
            ) values (
              RRL_TOPO_CHANGE_LOG_SQ.nextval, :topology_id, :entity_kind, :entity_id, :change_kind,
              :old_value_json, :new_value_json, substr(:user_id, 1, 50)
            )
            """,
            {
                "topology_id": topology_id,
                "entity_kind": entity_kind,
                "entity_id": entity_id,
                "change_kind": change_kind,
                "old_value_json": _json_text(old_value),
                "new_value_json": _json_text(new_value),
                "user_id": user,
            },
        )

    @staticmethod
    def _distance(prev: dict[str, Any] | None, cell: dict[str, Any]) -> float:
        if not prev:
            return 0
        dx = float(cell.get("x") or 0) - float(prev.get("x") or 0)
        dy = float(cell.get("y") or 0) - float(prev.get("y") or 0)
        return round((dx * dx + dy * dy) ** 0.5, 2)

    @staticmethod
    def _gate_distance(cell: dict[str, Any], gate: dict[str, Any]) -> float:
        # Manhattan distance is the MVP approximation: travel follows aisles/cross-aisles, not a direct diagonal.
        dx = abs(float(cell.get("x") or 0) - float(gate.get("x") or 0))
        dy = abs(float(cell.get("y") or 0) - float(gate.get("y") or 0))
        return round(dx + dy, 2)


def _json_text(value: Any) -> str | None:
    if value is None:
        return None
    import json

    return json.dumps(value, ensure_ascii=False, default=str)[:4000]
