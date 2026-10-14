"""Existing CASE metadata actions extracted without a reverse legacy-service dependency."""
from typing import Any, Callable
from fastapi import HTTPException
from ....schemas import CasePickTaskActionRequest,CasePickTransferRequest
from .case_assignment import context as resource_context,run_action
from .case_handoff import validate as validate_handoff

class CaseActions:
    def __init__(self,gateway: Any,event_writer: Callable[...,None]) -> None:
        self.gateway,self.event_writer=gateway,event_writer

    def _event(self,*args: Any) -> None:
        self.event_writer(self.gateway,*args)

    def claim_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None:
        ctx=resource_context(self.gateway,case_pick_task_id,"CLAIM",request)
        request=request.model_copy(update={key:ctx[key] for key in ("resource_id","resource_session_id","equipment_id")})
        actor = request.actor or "TSD"
        updated = self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK
               set STATUS = case when STATUS = 'NEW' then 'ASSIGNED' else STATUS end,
                   ASSIGNED_RESOURCE_ID = nvl(:resource_id, ASSIGNED_RESOURCE_ID),
                   RESOURCE_SESSION_ID = nvl(:resource_session_id, RESOURCE_SESSION_ID),
                   EQUIPMENT_ID = nvl(:equipment_id, EQUIPMENT_ID),
                   ASSIGNED_TO = :assignee,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_TASK_ID = :case_pick_task_id
               and STATUS in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT')
               and (ASSIGNED_RESOURCE_ID is null or ASSIGNED_RESOURCE_ID = :resource_id or :resource_id is null)
            """,
            {
                "case_pick_task_id": case_pick_task_id,
                "resource_id": request.resource_id,
                "resource_session_id": request.resource_session_id,
                "equipment_id": request.equipment_id,
                "actor": actor, "assignee":ctx["assigned_to"],
            },
        )
        if updated == 0:
            raise HTTPException(status_code=409, detail="Case-pick task cannot be claimed.")
        self._event(case_pick_task_id, None, "CLAIMED", request, actor)

    def start_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> None:
        ctx=resource_context(self.gateway,case_pick_task_id,"START",request)
        current=self.gateway.fetch_all("select STARTED_AT from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",{"id":case_pick_task_id})
        if current and current[0]["started_at"] is not None: return
        actor = request.actor or "TSD"
        self.claim_task(case_pick_task_id, request)
        self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK t
               set STATUS = case when STATUS='ASSIGNED' then 'IN_PROGRESS' else STATUS end,
                   STARTED_AT = nvl(STARTED_AT, systimestamp),
                   STARTED_AT_INSTANT = systimestamp,
                   STARTED_SHIFT_TIME_ZONE = null,
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_TASK_ID = :case_pick_task_id
               and STATUS in ('ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT')
            """,
            {"case_pick_task_id": case_pick_task_id, "actor": actor},
        )
        self._event(case_pick_task_id, None, "STARTED", request, actor)

    def transfer_task(self, case_pick_task_id: int, request: CasePickTransferRequest) -> None:
        validate_handoff(self.gateway,case_pick_task_id,request)
        ctx=resource_context(self.gateway,case_pick_task_id,"TRANSFER",request)
        assignee=ctx["assigned_to"]
        actor = request.actor or "SHIFT_LEAD"
        updated = self.gateway.execute(
            """
            update RRL_CASE_PICK_TASK
               set STATUS = case when STATUS = 'NEW' then 'ASSIGNED' else STATUS end,
                   ASSIGNED_RESOURCE_ID = :to_resource_id,
                   RESOURCE_SESSION_ID = :to_resource_session_id,
                   EQUIPMENT_ID = :to_equipment_id,
                   ASSIGNED_TO = :assignee,
                   TRANSFERRED_AT = systimestamp,
                   TRANSFERRED_BY = substr(:actor, 1, 100),
                   TRANSFER_REASON = substr(:reason, 1, 1000),
                   UPDATED_AT = systimestamp,
                   UPDATED_BY = substr(:actor, 1, 100)
             where CASE_PICK_TASK_ID = :case_pick_task_id
               and STATUS in ('NEW', 'ASSIGNED', 'IN_PROGRESS', 'PARTIAL', 'WAIT_REPLENISHMENT')
            """,
            {
                "case_pick_task_id": case_pick_task_id,
                "to_resource_id": ctx["resource_id"],
                "to_resource_session_id": ctx["resource_session_id"],
                "to_equipment_id": ctx["equipment_id"],
                "reason": request.reason,
                "actor": actor,"assignee":assignee,
            },
        )
        if updated == 0:
            raise HTTPException(status_code=409, detail="Case-pick task cannot be transferred.")
        self._event(case_pick_task_id, None, "TRANSFERRED", request, actor)


def execute(gateway: Any,task_id: int,action: str,request: Any,event_writer: Callable[...,None]) -> None:
    if action not in {"claim_task","start_task","transfer_task"}:raise ValueError("Unknown CASE metadata action")
    if getattr(gateway,"transaction_bound",False):
        getattr(CaseActions(gateway,event_writer),action)(task_id,request)
    else:
        run_action(gateway,task_id,action,request,
            lambda bound,task,req:getattr(CaseActions(bound,event_writer),action)(task,req))
