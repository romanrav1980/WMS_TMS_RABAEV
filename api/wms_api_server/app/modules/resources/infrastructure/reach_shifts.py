"""Store MAIN/DUTY roles in existing resource shifts; retain native session eligibility."""
from datetime import timedelta
from typing import Any
from fastapi import HTTPException

class ReachShifts:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def read(self, base_shift_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all("""select SHIFT_ID,SHIFT_CODE,WARE_ID,START_AT,FINISH_AT,
            STATUS,REACH_SHIFT_ROLE,EXPECTED_DRIVERS from RRL_RESOURCE_SHIFT
            where BASE_SHIFT_ID=:base order by case REACH_SHIFT_ROLE when 'MAIN' then 0 else 1 end,SHIFT_ID""",
            {"base": base_shift_id})
        return {"base_shift_id": base_shift_id, "shifts": rows,
                "main_offset_hours": -2, "duty_ends_with_warehouse_shift": True}

    def create(self, base_shift_id: int, main_drivers: int, duty_drivers: int, actor: str) -> dict[str, Any]:
        with self.gateway.transaction("Derive reachtruck shifts from warehouse shift") as cursor:
            cursor.execute("select RRL_HAS_WRIGHT(:actor,'resource_shift_edit') from dual", {"actor": actor})
            if cursor.fetchone()[0] != 1:
                raise HTTPException(403, detail="resource_shift_edit permission required")
            cursor.execute("""select WARE_ID,START_AT,FINISH_AT,STATUS,REACH_SHIFT_ROLE,SITE_CODE
                from RRL_RESOURCE_SHIFT where SHIFT_ID=:base for update""", {"base": base_shift_id})
            base = cursor.fetchone()
            if base is None:
                raise HTTPException(404, detail="Warehouse shift not found")
            ware, start, finish, status, role, site = base
            if role != "GENERAL" or ware is None or start is None or finish is None or finish <= start or status not in {"PLANNED", "OPEN"}:
                raise HTTPException(409, detail="Use an open or planned warehouse shift with valid times")
            cursor.execute("""select REACH_SHIFT_ROLE,EXPECTED_DRIVERS from RRL_RESOURCE_SHIFT
                where BASE_SHIFT_ID=:base order by REACH_SHIFT_ROLE""", {"base": base_shift_id})
            old = cursor.fetchall()
            expected = [("DUTY", duty_drivers), ("MAIN", main_drivers)]
            if old and old != expected:
                raise HTTPException(409, detail="Reach shifts already exist with different driver counts")
            if not old:
                for role, drivers, offset in (("MAIN", main_drivers, timedelta(hours=2)), ("DUTY", duty_drivers, timedelta(0))):
                    begins, ends = start - offset, finish - offset
                    cursor.execute("""insert into RRL_RESOURCE_SHIFT(SHIFT_ID,SHIFT_CODE,SHIFT_DATE,WARE_ID,SITE_CODE,
                        START_AT,FINISH_AT,STATUS,CREATED_BY,BASE_SHIFT_ID,REACH_SHIFT_ROLE,EXPECTED_DRIVERS)
                        values(RRL_RESOURCE_SHIFT_SQ.nextval,:code,:day,:ware,:site,:begins,:ends,:status,:actor,:base,:role,:drivers)""",
                        {"code": f"REACH:{base_shift_id}:{role}", "day": begins.date(), "ware": ware, "site": site,
                         "begins": begins, "ends": ends, "status": status, "actor": actor,
                         "base": base_shift_id, "role": role, "drivers": drivers})
        return self.read(base_shift_id)
