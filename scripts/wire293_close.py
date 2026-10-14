from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
s+='''

    def close_incident(self,operation: str,body: dict,actor: str) -> dict:
        from .interwarehouse_incident_close import close_incident
        return close_incident(self.gateway,operation,body,actor)
'''
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8").replace("class InterwarehousePort(Protocol):","class InterwarehousePort(Protocol):\n    def close_incident(self,operation: str,body: dict,actor: str) -> dict[str,Any]: ...");out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
s+='''

class IncidentClosure(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    incident_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    incident_revision: int=Field(strict=True,ge=1)
    followup_receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    reason: str=Field(strict=True,min_length=8,max_length=500)
    evidence_reference: str=Field(strict=True,min_length=1,max_length=255)

@router.post("/incident-closures")
def close_incident(body: IncidentClosure,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                   service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    try:return service.close_incident(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409})from exc
'''
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.sql");s=p.read_text(encoding="utf-8")
needle=" p.TARGET_TT_ID ORIGINAL_TARGET_TRIP_ID,"
assert needle in s;s=s.replace(needle," incident_close.OPERATION_ID INCIDENT_CLOSE_OPERATION_ID,incident_close.REASON_TEXT INCIDENT_CLOSE_REASON,incident_close.EVIDENCE_REFERENCE INCIDENT_CLOSE_EVIDENCE,\n to_char(incident_close.CLOSED_AT,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM')INCIDENT_CLOSED_AT,\n"+needle,1)
needle="join RRL_TRANSPORT_TASK t on"
assert needle in s;s=s.replace(needle,"left join RRL_INTERWARE_INCIDENT_CLOSE incident_close on incident_close.INCIDENT_OPERATION_ID=incident.OPERATION_ID\n"+needle,1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_decisions.py");s=p.read_text(encoding="utf-8")
needle="                to_char(d.CREATED_AT"
assert needle in s;s=s.replace(needle,"""                closed.OPERATION_ID INCIDENT_CLOSE_OPERATION_ID,closed.REASON_TEXT INCIDENT_CLOSE_REASON,closed.EVIDENCE_REFERENCE INCIDENT_CLOSE_EVIDENCE,
                to_char(closed.CLOSED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')INCIDENT_CLOSED_AT,
"""+needle,1)
s=s.replace("where d.PLAN_OPERATION_ID=:plan and d.REVISION_NO>:after_revision","left join RRL_INTERWARE_INCIDENT_CLOSE closed on closed.INCIDENT_OPERATION_ID=d.OPERATION_ID where d.PLAN_OPERATION_ID=:plan and d.REVISION_NO>:after_revision")
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
