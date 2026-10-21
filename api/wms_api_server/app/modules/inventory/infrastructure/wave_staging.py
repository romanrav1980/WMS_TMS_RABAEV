"""Atomic release of existing FULL_PALLET tasks; physical posting stays in Root."""
from typing import Any
import oracledb
from ..contracts_wave_planning import WavePlanningError


def _target(cursor: Any, wave: int, cell: str, actor: str) -> None:
    cursor.execute("select STATUS,WARE_ID from RRL_PICK_WAVE where PICK_WAVE_ID=:wave for update nowait", wave=wave)
    row = cursor.fetchone()
    if not row:
        raise WavePlanningError("PICK_WAVE_NOT_FOUND", 404)
    if row[0] != "LAUNCHED":
        raise WavePlanningError("STAGING_REQUIRES_LAUNCHED_WAVE", 409)
    cursor.execute("""select count(*) from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
        and RRL_HAS_WRIGHT(u.ID,'pick_wave_launch')=1
        and(u.WARE_ID=:ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""", actor=actor, ware=row[1])
    if cursor.fetchone()[0] != 1:
        raise WavePlanningError("WAVE_CURRENT_WAREHOUSE_REQUIRED", 403)
    cursor.execute("select WARE_ID from RRL_CELLS where CELL=:cell", cell=cell)
    target = cursor.fetchone()
    if not target or target[0] != row[1]:
        raise WavePlanningError("STAGING_TARGET_WAREHOUSE_MISMATCH", 409)


def _release(cursor: Any, wave: int, cell: str, actor: str) -> int:
    cursor.execute("""select PICK_WAVE_TASK_ID,PALLET_UID,ARTICUL,SOURCE_CELL_CODE,QTY
        from RRL_PICK_WAVE_TASK where PICK_WAVE_ID=:wave and TASK_TYPE='FULL_PALLET'
        and STATUS in('NEW','ASSIGNED') order by PICK_WAVE_TASK_ID for update nowait""", wave=wave)
    rows = cursor.fetchmany(201)
    if len(rows) > 200:
        raise WavePlanningError("STAGING_BATCH_BOUND_200", 409)
    count = 0
    for task, uid, article, source, quantity in rows:
        if not uid or not source or not quantity or quantity <= 0 or source == cell:
            raise WavePlanningError("STAGING_SOURCE_REQUIRED", 409)
        cursor.execute("""select TASK_ID,TO_CELL from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'
            and TASK_TYPE='PICKING_MOVE' and SOURCE_DOC_TYPE='PICK_WAVE'
            and SOURCE_TASK_ID=:task and STATUS<>'CANCELLED'""", task=task)
        existing = cursor.fetchmany(2)
        if len(existing) > 1 or (existing and existing[0][1] != cell):
            raise WavePlanningError("STAGING_EXISTING_TARGET_CONFLICT", 409)
        if not existing:
            cursor.execute("""insert into RRL_WAREHOUSE_TASK
                (TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,
                 TARGET_ARTICUL,UID_PALLET,SSCC,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,
                 PRIORITY,STATUS,CREATED_AT,CREATED_BY)
                select RRL_WAREHOUSE_TASK_SQ.nextval,'PICKING_MOVE','WAVE',:task,'PICK_WAVE',
                 :wave,:article,:pallet,p.SSCC,:source,:target,src.WARE_ID,dst.WARE_ID,:qty,r.BASE_UOM,'PALLET',
                 90,'PLANNED',systimestamp,substr(:actor,1,100)
                from RRL_PALLETS p join RRL_REMAINS r on r.UID_POLETA=p.UID_PALLET
                 join RRL_CELLS src on src.CELL=r.CELL join RRL_CELLS dst on dst.CELL=:target
                where p.UID_PALLET=:pallet and p.ARTICUL=:article and r.CELL=:source""",
                task=task, wave=wave, article=article, pallet=uid, source=source,
                target=cell, qty=quantity, actor=actor)
            if cursor.rowcount != 1:
                raise WavePlanningError("STAGING_CURRENT_SOURCE_REQUIRED", 409)
            count += 1
        cursor.execute("""update RRL_PICK_WAVE_TASK set STATUS='ASSIGNED',TARGET_CELL_CODE=:cell,
            UPDATED_AT=sysdate,UPDATED_BY=substr(:actor,1,50) where PICK_WAVE_TASK_ID=:task""",
            cell=cell, actor=actor, task=task)
    return count


def release_staging(gateway: Any, wave: int, request: Any) -> int:
    cell = str(request.to_cell or "").strip()
    if not cell:
        raise WavePlanningError("STAGING_TARGET_REQUIRED", 422)
    try:
        with gateway.transaction("Release existing full-pallet staging tasks atomically") as cursor:
            _target(cursor, wave, cell, request.updated_by)
            return _release(cursor, wave, cell, request.updated_by)
    except oracledb.Error as exc:
        if getattr(exc.args[0], "code", None) in {1, 54, 60}:
            raise WavePlanningError("STAGING_CHANGED_RETRY", 409) from exc
        raise
