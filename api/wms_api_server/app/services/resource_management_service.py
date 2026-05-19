from typing import Any

from fastapi import HTTPException

from ..oracle_gateway import OracleGateway
from ..schemas import (
    ResourceCreateRequest,
    ResourceEquipmentCreateRequest,
    ResourceSessionLoginRequest,
    ResourceSessionStatusRequest,
    ResourceShiftCreateRequest,
    ResourceTsdLoginRequest,
)
from .mes_service import clamp_limit


class ResourceManagementService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_resource_types(self, active: int | None = 1) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {}
        if active is not None:
            conditions.append("ACTIVE = :active")
            params["active"] = 1 if int(active) == 1 else 0
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select RESOURCE_TYPE, RESOURCE_CLASS, RESOURCE_NAME,
                   DEFAULT_TASK_TYPES, ACTIVE, CREATED_AT, UPDATED_AT
              from RRL_RESOURCE_TYPE
              {where_sql}
             order by RESOURCE_CLASS, RESOURCE_TYPE
            """,
            params,
        )

    def list_equipment(
        self,
        equipment_type: str | None = None,
        service_status: str | None = None,
        active: int | None = 1,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if equipment_type:
            conditions.append("EQUIPMENT_TYPE = :equipment_type")
            params["equipment_type"] = equipment_type.upper()
        if service_status:
            conditions.append("SERVICE_STATUS = :service_status")
            params["service_status"] = service_status.upper()
        if active is not None:
            conditions.append("ACTIVE = :active")
            params["active"] = 1 if int(active) == 1 else 0
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select EQUIPMENT_ID, EQUIPMENT_CODE, EQUIPMENT_TYPE,
                       EQUIPMENT_NAME, WARE_ID, HOME_ZONE_CODE,
                       CAPACITY_CLASS, SERVICE_STATUS, ACTIVE,
                       CREATED_AT, CREATED_BY, UPDATED_AT, UPDATED_BY
                  from RRL_RESOURCE_EQUIPMENT
                  {where_sql}
                 order by EQUIPMENT_TYPE, EQUIPMENT_CODE
              )
             where rownum <= :limit
            """,
            params,
        )

    def create_equipment(self, request: ResourceEquipmentCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              insert into RRL_RESOURCE_EQUIPMENT (
                EQUIPMENT_ID, EQUIPMENT_CODE, EQUIPMENT_TYPE, EQUIPMENT_NAME,
                WARE_ID, HOME_ZONE_CODE, CAPACITY_CLASS, SERVICE_STATUS,
                ACTIVE, CREATED_BY
              ) values (
                RRL_RESOURCE_EQUIPMENT_SQ.nextval, :equipment_code,
                :equipment_type, :equipment_name, :ware_id, :home_zone_code,
                :capacity_class, :service_status, :active, :created_by
              )
              returning EQUIPMENT_ID into :result;
            end;
            """,
            {
                "equipment_code": request.equipment_code,
                "equipment_type": request.equipment_type.upper(),
                "equipment_name": request.equipment_name,
                "ware_id": request.ware_id,
                "home_zone_code": request.home_zone_code,
                "capacity_class": request.capacity_class,
                "service_status": (request.service_status or "ACTIVE").upper(),
                "active": 1 if int(request.active) == 1 else 0,
                "created_by": request.created_by,
            },
        )

    def list_resources(
        self,
        resource_type: str | None = None,
        resource_class: str | None = None,
        status: str | None = None,
        ware_id: int | None = None,
        zone_code: str | None = None,
        active: int | None = 1,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if resource_type:
            conditions.append("r.RESOURCE_TYPE = :resource_type")
            params["resource_type"] = resource_type.upper()
        if resource_class:
            conditions.append("r.RESOURCE_CLASS = :resource_class")
            params["resource_class"] = resource_class.upper()
        if status:
            conditions.append("r.STATUS = :status")
            params["status"] = status.upper()
        if ware_id is not None:
            conditions.append("r.WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if zone_code:
            conditions.append("upper(r.ZONE_CODE) = :zone_code")
            params["zone_code"] = zone_code.upper()
        if active is not None:
            conditions.append("r.ACTIVE = :active")
            params["active"] = 1 if int(active) == 1 else 0
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select r.RESOURCE_ID, r.RESOURCE_CODE, r.RESOURCE_NAME,
                       r.RESOURCE_CLASS, r.RESOURCE_TYPE, rt.RESOURCE_NAME RESOURCE_TYPE_NAME,
                       r.EQUIPMENT_ID, e.EQUIPMENT_CODE, e.EQUIPMENT_NAME,
                       r.USER_ID, r.TEAM_CODE, r.WARE_ID, r.ZONE_CODE,
                       r.STATUS, r.ACTIVE, r.CREATED_AT, r.CREATED_BY,
                       r.UPDATED_AT, r.UPDATED_BY,
                       s.SESSION_ID ACTIVE_SESSION_ID,
                       s.OPERATOR_USER_ID ACTIVE_OPERATOR_USER_ID,
                       s.LOGIN_AT ACTIVE_LOGIN_AT,
                       s.LAST_HEARTBEAT_AT ACTIVE_HEARTBEAT_AT,
                       s.CURRENT_TASK_ID ACTIVE_TASK_ID
                  from RRL_RESOURCE r
                  join RRL_RESOURCE_TYPE rt on rt.RESOURCE_TYPE = r.RESOURCE_TYPE
                  left join RRL_RESOURCE_EQUIPMENT e on e.EQUIPMENT_ID = r.EQUIPMENT_ID
                  left join RRL_RESOURCE_SESSION s
                    on s.RESOURCE_ID = r.RESOURCE_ID
                   and s.STATUS in ('ACTIVE', 'PAUSED')
                  {where_sql}
                 order by r.RESOURCE_TYPE, r.RESOURCE_CODE
              )
             where rownum <= :limit
            """,
            params,
        )

    def create_resource(self, request: ResourceCreateRequest) -> int:
        resource_type = request.resource_type.upper()
        resource_class = request.resource_class.upper() if request.resource_class else self._get_resource_class(resource_type)
        return self.gateway.call_number_plsql(
            """
            begin
              insert into RRL_RESOURCE (
                RESOURCE_ID, RESOURCE_CODE, RESOURCE_NAME, RESOURCE_CLASS,
                RESOURCE_TYPE, EQUIPMENT_ID, USER_ID, TEAM_CODE, WARE_ID,
                ZONE_CODE, STATUS, ACTIVE, CREATED_BY
              ) values (
                RRL_RESOURCE_SQ.nextval, :resource_code, :resource_name,
                :resource_class, :resource_type, :equipment_id, :user_id,
                :team_code, :ware_id, :zone_code, :status, :active,
                :created_by
              )
              returning RESOURCE_ID into :result;
            end;
            """,
            {
                "resource_code": request.resource_code,
                "resource_name": request.resource_name,
                "resource_class": resource_class,
                "resource_type": resource_type,
                "equipment_id": request.equipment_id,
                "user_id": request.user_id,
                "team_code": request.team_code,
                "ware_id": request.ware_id,
                "zone_code": request.zone_code,
                "status": (request.status or "AVAILABLE").upper(),
                "active": 1 if int(request.active) == 1 else 0,
                "created_by": request.created_by,
            },
        )

    def list_shifts(
        self,
        shift_date: str | None = None,
        ware_id: int | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if shift_date:
            conditions.append("SHIFT_DATE = to_date(:shift_date, 'YYYY-MM-DD')")
            params["shift_date"] = shift_date
        if ware_id is not None:
            conditions.append("WARE_ID = :ware_id")
            params["ware_id"] = ware_id
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select SHIFT_ID, SHIFT_CODE, SHIFT_DATE, WARE_ID, SITE_CODE,
                       START_AT, FINISH_AT, STATUS, CREATED_AT, CREATED_BY,
                       UPDATED_AT, UPDATED_BY
                  from RRL_RESOURCE_SHIFT
                  {where_sql}
                 order by SHIFT_DATE desc, START_AT, SHIFT_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def create_shift(self, request: ResourceShiftCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              insert into RRL_RESOURCE_SHIFT (
                SHIFT_ID, SHIFT_CODE, SHIFT_DATE, WARE_ID, SITE_CODE,
                START_AT, FINISH_AT, STATUS, CREATED_BY
              ) values (
                RRL_RESOURCE_SHIFT_SQ.nextval, :shift_code, :shift_date,
                :ware_id, :site_code, :start_at, :finish_at, :status,
                :created_by
              )
              returning SHIFT_ID into :result;
            end;
            """,
            {
                "shift_code": request.shift_code,
                "shift_date": request.shift_date,
                "ware_id": request.ware_id,
                "site_code": request.site_code,
                "start_at": request.start_at,
                "finish_at": request.finish_at,
                "status": (request.status or "PLANNED").upper(),
                "created_by": request.created_by,
            },
        )

    def list_sessions(
        self,
        session_id: int | None = None,
        shift_id: int | None = None,
        resource_id: int | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": clamp_limit(limit)}
        if session_id is not None:
            conditions.append("s.SESSION_ID = :session_id")
            params["session_id"] = session_id
        if shift_id is not None:
            conditions.append("s.SHIFT_ID = :shift_id")
            params["shift_id"] = shift_id
        if resource_id is not None:
            conditions.append("s.RESOURCE_ID = :resource_id")
            params["resource_id"] = resource_id
        if status:
            conditions.append("s.STATUS = :status")
            params["status"] = status.upper()
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select s.SESSION_ID, s.SHIFT_ID, s.RESOURCE_ID,
                       r.RESOURCE_CODE, r.RESOURCE_NAME, r.RESOURCE_TYPE,
                       s.EQUIPMENT_ID, e.EQUIPMENT_CODE, s.OPERATOR_USER_ID,
                       s.LOGIN_AT, s.LOGOUT_AT, s.STATUS, s.CURRENT_TASK_ID,
                       s.LAST_HEARTBEAT_AT, s.TERMINAL_ID, s.ZONE_CODE,
                       s.CREATED_BY, s.CLOSED_BY
                  from RRL_RESOURCE_SESSION s
                  join RRL_RESOURCE r on r.RESOURCE_ID = s.RESOURCE_ID
                  left join RRL_RESOURCE_EQUIPMENT e on e.EQUIPMENT_ID = s.EQUIPMENT_ID
                  {where_sql}
                 order by s.LOGIN_AT desc, s.SESSION_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def login_session(self, request: ResourceSessionLoginRequest) -> int:
        resource = self._get_resource(request.resource_id)
        equipment_id = request.equipment_id if request.equipment_id is not None else resource.get("equipment_id")
        return self.gateway.call_number_plsql(
            """
            begin
              insert into RRL_RESOURCE_SESSION (
                SESSION_ID, SHIFT_ID, RESOURCE_ID, EQUIPMENT_ID,
                OPERATOR_USER_ID, LOGIN_AT, STATUS, LAST_HEARTBEAT_AT,
                TERMINAL_ID, ZONE_CODE, CREATED_BY
              ) values (
                RRL_RESOURCE_SESSION_SQ.nextval, :shift_id, :resource_id,
                :equipment_id, :operator_user_id, systimestamp, 'ACTIVE',
                systimestamp, :terminal_id, :zone_code, :created_by
              )
              returning SESSION_ID into :result;
            end;
            """,
            {
                "shift_id": request.shift_id,
                "resource_id": request.resource_id,
                "equipment_id": equipment_id,
                "operator_user_id": request.operator_user_id or resource.get("user_id"),
                "terminal_id": request.terminal_id,
                "zone_code": request.zone_code or resource.get("zone_code"),
                "created_by": request.created_by,
            },
        )

    def login_tsd(self, request: ResourceTsdLoginRequest) -> dict[str, Any]:
        driver_code = (request.driver_code or request.barcode or "").strip()
        barcode = (request.barcode or "").strip()
        if not driver_code and not barcode:
            raise HTTPException(status_code=400, detail="driver_code or barcode is required.")
        if request.password:
            self._validate_legacy_user_password(driver_code, request.password)

        resource = self._resolve_tsd_resource(driver_code=driver_code, barcode=barcode)
        equipment = self._resolve_equipment(request.equipment_code, resource.get("equipment_id"))
        shift = self._resolve_active_shift(request.ware_id or resource.get("ware_id"))
        operator_user_id = str(resource.get("user_id") or driver_code or barcode)
        existing = self._find_active_session(
            resource_id=int(resource["resource_id"]),
            equipment_id=int(equipment["equipment_id"]) if equipment else resource.get("equipment_id"),
            operator_user_id=operator_user_id,
        )
        if existing:
            same_resource = int(existing.get("resource_id") or -1) == int(resource["resource_id"])
            same_operator = str(existing.get("operator_user_id") or "").upper() == operator_user_id.upper()
            if not (same_resource or same_operator):
                raise HTTPException(status_code=409, detail="Equipment is already used by another active session.")
            return {
                "session_id": existing["session_id"],
                "resource_id": resource["resource_id"],
                "resource_code": resource["resource_code"],
                "resource_name": resource["resource_name"],
                "resource_type": resource["resource_type"],
                "equipment_id": existing.get("equipment_id"),
                "equipment_code": existing.get("equipment_code"),
                "operator_user_id": existing.get("operator_user_id") or operator_user_id,
                "shift_id": existing["shift_id"],
                "shift_code": shift["shift_code"],
                "status": existing["status"],
            }
        session_id = self.login_session(
            ResourceSessionLoginRequest(
                shift_id=int(shift["shift_id"]),
                resource_id=int(resource["resource_id"]),
                equipment_id=int(equipment["equipment_id"]) if equipment else resource.get("equipment_id"),
                operator_user_id=operator_user_id,
                terminal_id=request.terminal_id,
                zone_code=request.zone_code or resource.get("zone_code"),
                created_by=operator_user_id,
            )
        )
        rows = self.list_sessions(session_id=session_id, limit=1)
        session = rows[0] if rows else {"session_id": session_id}
        return {
            "session_id": session_id,
            "resource_id": resource["resource_id"],
            "resource_code": resource["resource_code"],
            "resource_name": resource["resource_name"],
            "resource_type": resource["resource_type"],
            "equipment_id": equipment.get("equipment_id") if equipment else resource.get("equipment_id"),
            "equipment_code": equipment.get("equipment_code") if equipment else None,
            "operator_user_id": session.get("operator_user_id") or operator_user_id,
            "shift_id": shift["shift_id"],
            "shift_code": shift["shift_code"],
            "status": "ACTIVE",
        }

    def heartbeat(self, session_id: int) -> None:
        updated = self.gateway.execute(
            """
            update RRL_RESOURCE_SESSION
               set LAST_HEARTBEAT_AT = systimestamp
             where SESSION_ID = :session_id
               and STATUS in ('ACTIVE', 'PAUSED')
            """,
            {"session_id": session_id},
        )
        if updated == 0:
            raise HTTPException(status_code=404, detail="Active resource session not found.")

    def pause_session(self, session_id: int, request: ResourceSessionStatusRequest) -> None:
        self._set_session_status(session_id, "PAUSED", request.updated_by)

    def resume_session(self, session_id: int, request: ResourceSessionStatusRequest) -> None:
        self._set_session_status(session_id, "ACTIVE", request.updated_by)

    def logout_session(self, session_id: int, request: ResourceSessionStatusRequest) -> None:
        updated = self.gateway.execute(
            """
            update RRL_RESOURCE_SESSION
               set STATUS = 'CLOSED',
                   LOGOUT_AT = systimestamp,
                   CLOSED_BY = :closed_by
             where SESSION_ID = :session_id
               and STATUS in ('ACTIVE', 'PAUSED', 'ERROR')
            """,
            {"session_id": session_id, "closed_by": request.updated_by},
        )
        if updated == 0:
            raise HTTPException(status_code=404, detail="Open resource session not found.")

    def _set_session_status(self, session_id: int, status: str, updated_by: str | None) -> None:
        updated = self.gateway.execute(
            """
            update RRL_RESOURCE_SESSION
               set STATUS = :status,
                   LAST_HEARTBEAT_AT = systimestamp,
                   CLOSED_BY = case when :status = 'CLOSED' then :updated_by else CLOSED_BY end
             where SESSION_ID = :session_id
               and STATUS in ('ACTIVE', 'PAUSED')
            """,
            {"session_id": session_id, "status": status, "updated_by": updated_by},
        )
        if updated == 0:
            raise HTTPException(status_code=404, detail="Active resource session not found.")

    def _get_resource_class(self, resource_type: str) -> str:
        rows = self.gateway.fetch_all(
            """
            select RESOURCE_CLASS
              from RRL_RESOURCE_TYPE
             where RESOURCE_TYPE = :resource_type
            """,
            {"resource_type": resource_type},
        )
        if not rows:
            raise HTTPException(status_code=400, detail=f"Unknown resource_type: {resource_type}")
        return str(rows[0].get("resource_class") or "")

    def _get_resource(self, resource_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select RESOURCE_ID, RESOURCE_CODE, RESOURCE_NAME, RESOURCE_TYPE,
                   EQUIPMENT_ID, USER_ID, WARE_ID, ZONE_CODE, STATUS, ACTIVE
              from RRL_RESOURCE
             where RESOURCE_ID = :resource_id
            """,
            {"resource_id": resource_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Resource not found.")
        row = rows[0]
        if int(row.get("active") or 0) != 1:
            raise HTTPException(status_code=409, detail="Resource is inactive.")
        return row

    def _resolve_tsd_resource(self, driver_code: str, barcode: str) -> dict[str, Any]:
        lookup = (driver_code or barcode).upper()
        rows = self.gateway.fetch_all(
            """
            select *
              from (
                select RESOURCE_ID, RESOURCE_CODE, RESOURCE_NAME, RESOURCE_TYPE,
                       EQUIPMENT_ID, USER_ID, WARE_ID, ZONE_CODE, STATUS, ACTIVE
                  from RRL_RESOURCE
                 where ACTIVE = 1
                   and RESOURCE_TYPE in ('REACHTRUCK', 'FORKLIFT', 'KIKA', 'TROLLEY', 'CASE_PICKER')
                   and (
                     upper(RESOURCE_CODE) = :lookup
                     or upper(nvl(USER_ID, '')) = :lookup
                     or upper(nvl(TEAM_CODE, '')) = :lookup
                   )
                 order by case when upper(nvl(USER_ID, '')) = :lookup then 1 else 2 end,
                          RESOURCE_ID
              )
             where rownum = 1
            """,
            {"lookup": lookup},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="TSD resource for driver/barcode not found.")
        return rows[0]

    def _resolve_equipment(self, equipment_code: str | None, default_equipment_id: Any) -> dict[str, Any] | None:
        if not equipment_code and default_equipment_id is None:
            return None
        if equipment_code:
            rows = self.gateway.fetch_all(
                """
                select EQUIPMENT_ID, EQUIPMENT_CODE, EQUIPMENT_TYPE, SERVICE_STATUS, ACTIVE
                  from RRL_RESOURCE_EQUIPMENT
                 where upper(EQUIPMENT_CODE) = :equipment_code
                """,
                {"equipment_code": equipment_code.upper()},
            )
        else:
            rows = self.gateway.fetch_all(
                """
                select EQUIPMENT_ID, EQUIPMENT_CODE, EQUIPMENT_TYPE, SERVICE_STATUS, ACTIVE
                  from RRL_RESOURCE_EQUIPMENT
                 where EQUIPMENT_ID = :equipment_id
                """,
                {"equipment_id": default_equipment_id},
            )
        if not rows:
            raise HTTPException(status_code=404, detail="Equipment not found.")
        row = rows[0]
        if int(row.get("active") or 0) != 1 or row.get("service_status") != "ACTIVE":
            raise HTTPException(status_code=409, detail="Equipment is not available.")
        return row

    def _resolve_active_shift(self, ware_id: Any | None) -> dict[str, Any]:
        params: dict[str, Any] = {"ware_id": ware_id}
        return_rows = self.gateway.fetch_all(
            """
            select *
              from (
                select SHIFT_ID, SHIFT_CODE, SHIFT_DATE, WARE_ID, START_AT, FINISH_AT, STATUS
                  from RRL_RESOURCE_SHIFT
                 where STATUS in ('PLANNED', 'OPEN')
                   and systimestamp between START_AT and FINISH_AT
                   and (:ware_id is null or WARE_ID = :ware_id or WARE_ID is null)
                 order by case when WARE_ID = :ware_id then 1 else 2 end,
                          START_AT desc
              )
             where rownum = 1
            """,
            params,
        )
        if not return_rows:
            raise HTTPException(status_code=404, detail="Active resource shift not found.")
        return return_rows[0]

    def _find_active_session(
        self,
        resource_id: int,
        equipment_id: int | None,
        operator_user_id: str,
    ) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select *
              from (
                select s.SESSION_ID, s.SHIFT_ID, s.RESOURCE_ID, s.EQUIPMENT_ID,
                       e.EQUIPMENT_CODE, s.OPERATOR_USER_ID, s.STATUS
                  from RRL_RESOURCE_SESSION s
                  left join RRL_RESOURCE_EQUIPMENT e on e.EQUIPMENT_ID = s.EQUIPMENT_ID
                 where s.STATUS in ('ACTIVE', 'PAUSED')
                   and (
                     s.RESOURCE_ID = :resource_id
                     or (:equipment_id is not null and s.EQUIPMENT_ID = :equipment_id)
                     or upper(nvl(s.OPERATOR_USER_ID, '')) = :operator_user_id
                   )
                 order by s.LOGIN_AT desc
              )
             where rownum = 1
            """,
            {
                "resource_id": resource_id,
                "equipment_id": equipment_id,
                "operator_user_id": operator_user_id.upper(),
            },
        )
        return rows[0] if rows else None

    def _validate_legacy_user_password(self, user_id: str, password: str) -> None:
        rows = self.gateway.fetch_all(
            """
            select ID
              from RUSERS
             where lower(ID) = lower(:user_id)
               and PASS = :password
               and nvl(DELETED, 0) = 0
            """,
            {"user_id": user_id, "password": password},
        )
        if not rows:
            raise HTTPException(status_code=401, detail="Invalid driver password.")
