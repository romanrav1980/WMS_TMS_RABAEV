"""Scoped metadata entry points delegating to the installed wave planner."""
from typing import Any
import oracledb
from ..contracts_wave_planning import WavePlanningError


def _scope(cursor: Any, warehouse: int | None, actor: str) -> None:
    if warehouse is None or warehouse < 1:
        raise WavePlanningError("WAVE_EXPLICIT_WAREHOUSE_REQUIRED", 422)
    cursor.execute("""select count(*) from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
        and RRL_HAS_WRIGHT(u.ID,'pick_wave_create')=1
        and (u.WARE_ID=:ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
        and exists(select 1 from RRL_WARES w where w.ID=:ware)""", actor=actor, ware=warehouse)
    if cursor.fetchone()[0] != 1:
        raise WavePlanningError("WAVE_CURRENT_WAREHOUSE_REQUIRED", 403)


def create_wave(gateway: Any, request: Any) -> int:
    with gateway.transaction("Existing wave creation in actor warehouse") as cursor:
        _scope(cursor, request.ware_id, request.created_by)
        return int(cursor.callfunc("RRL_PICK_WAVE_API.create_wave", oracledb.DB_TYPE_NUMBER,
            keyword_parameters={"p_"+key:value for key,value in request.model_dump().items()}))


def add_plan(gateway: Any, wave: int, request: Any) -> None:
    try:
        with gateway.transaction("Existing wave plan binding") as cursor:
            # Serialize competing assignments of one plan before taking a wave lock.
            cursor.execute("select WARE_ID from RRL_PICK_PLAN where PICK_PLAN_ID=:plan for update nowait",
                           plan=request.pick_plan_id)
            plan = cursor.fetchone()
            if plan is None:
                raise WavePlanningError("PICK_PLAN_NOT_FOUND", 404)
            _scope(cursor, plan[0], request.created_by)
            cursor.execute("select WARE_ID from RRL_PICK_WAVE where PICK_WAVE_ID=:wave", wave=wave)
            target = cursor.fetchone()
            if target is None:
                raise WavePlanningError("PICK_WAVE_NOT_FOUND", 404)
            _scope(cursor, target[0], request.created_by)
            if target[0] != plan[0]:
                raise WavePlanningError("PICK_PLAN_WAVE_WAREHOUSE_MISMATCH", 409)
            cursor.callproc("RRL_PICK_WAVE_API.add_plan", [wave, request.pick_plan_id, request.created_by])
    except oracledb.Error as exc:
        code = getattr(exc.args[0], "code", None)
        if code in {54, 60, 20990, 20991, 20992, 20993, 20994}:
            raise WavePlanningError(str(exc.args[0]).split("\n", 1)[0], 409) from exc
        raise
