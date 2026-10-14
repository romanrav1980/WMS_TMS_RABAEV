"""Original CASE state, lines and physical lots; metadata only, one existing UOW."""
import json
from typing import Any, Callable
from fastapi import HTTPException
from .metadata_transactions import receipt_task_metadata
from .case_close_journal import close_replay, record_close
from ..domain.case_close_state import close_transition


def validate_close_content(cur: Any, task: int, actor: str, assignee: str | None) -> None:
    if assignee is not None and assignee != actor:
        cur.execute("select RRL_HAS_WRIGHT(:actor,'case_pick_manage')from dual", actor=actor)
        if cur.fetchone()[0] != 1:
            raise HTTPException(409, detail="CASE_TASK_ACTOR_CONFLICT")
    cur.execute("""select count(*)from RRL_CASE_PICK_SHORT where CASE_PICK_TASK_ID=:id
        and STATUS in('CREATED','PENDING_APPROVAL')""", id=task)
    if cur.fetchone()[0]:
        raise HTTPException(409, detail="CASE_PENDING_SHORT_DECISION_REQUIRED")
    cur.execute("""select count(*)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id
        and (STATUS is null or STATUS not in('PICKED','SHORT_PICKED','CANCELLED'))""", id=task)
    if cur.fetchone()[0]:
        raise HTTPException(409, detail="CASE_OPEN_LINES_REMAIN")
    cur.execute("""select count(*)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id
        and (nvl(PICKED_QTY,0)<0 or nvl(PLANNED_QTY,0)<0 or nvl(PICKED_QTY,0)>nvl(PLANNED_QTY,0)
             or(STATUS='PICKED'and nvl(PICKED_QTY,0)!=nvl(PLANNED_QTY,0)))""", id=task)
    if cur.fetchone()[0]:
        raise HTTPException(409, detail="CASE_LINE_QUANTITY_STATE_CONFLICT")
    cur.execute("""select count(*)from RRL_CASE_PICK_LINE l
        left join(select h.CASE_PICK_LINE_ID,sum(s.REMAIN) QTY from RRL_CASE_CARRIER_LOT h
          join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:id
          group by h.CASE_PICK_LINE_ID)p on p.CASE_PICK_LINE_ID=l.CASE_PICK_LINE_ID
        where l.CASE_PICK_TASK_ID=:id and nvl(p.QTY,0)!=nvl(l.PICKED_QTY,0)""", id=task)
    if cur.fetchone()[0]:
        raise HTTPException(409, detail="CASE_PHYSICAL_QUANTITY_MISMATCH")


def close_case_carrier(
    gateway: Any, task: int, request: Any, assert_scope: Callable[[Any,int,str,str],None],
) -> dict[str, Any]:
    actor = request.actor
    body = request.model_dump(mode="json")
    operation = getattr(request, "operation_id", None)
    if len(json.dumps(body, ensure_ascii=True).encode()) > 16384:
        raise HTTPException(422, detail="CASE_CLOSE_REQUEST_BOUND_16KB")
    with receipt_task_metadata(gateway, "Existing CASE carrier close", actor, "case_pick_execute") as cur:
        assert_scope(cur, task, actor, "case_pick_execute")
        cur.execute("""select STATUS,nvl(CONTENT_VERSION,0),ASSIGNED_TO,SHIPPED_OPERATION
            from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id for update""", id=task)
        status,version,assignee,shipped = cur.fetchone()
        assert_scope(cur, task, actor, "case_pick_execute")
        replay = close_replay(cur, operation, task, actor, body)
        if replay is not None:
            return replay
        expected = getattr(request, "expected_content_version", None)
        if expected is not None and expected != version:
            raise HTTPException(409, detail="CASE_CONTENT_VERSION_CHANGED")
        transition = close_transition(status, shipped)
        if transition not in ("CLOSE", "ALREADY_CLOSED"):
            raise HTTPException(409, detail="CASE_CLOSE_" + transition)
        if transition == "ALREADY_CLOSED":
            result = {"status": status, "content_version": version, "already_closed": True, "physical_stock_changed": False}
            if operation is not None:
                record_close(cur, operation, task, actor, body, result)
            return result
        validate_close_content(cur, task, actor, assignee)
        cur.execute("""update RRL_CASE_PICK_TASK t
            set(TOTAL_LINES,PICKED_LINES,PLANNED_QTY,PICKED_QTY)=(
              select count(*),sum(case when STATUS in('PICKED','SHORT_PICKED','CANCELLED')then 1 else 0 end),
                     nvl(sum(PLANNED_QTY),0),nvl(sum(PICKED_QTY),0)
              from RRL_CASE_PICK_LINE l where l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID),
                STATUS='WAIT_CONTROL',CLOSED_AT=systimestamp,UPDATED_AT=systimestamp,UPDATED_BY=:actor
            where CASE_PICK_TASK_ID=:id""", actor=actor,id=task)
        result = {"status": "WAIT_CONTROL", "content_version": version, "already_closed": False, "physical_stock_changed": False}
        record_close(cur, operation, task, actor, body, result)
        return result
