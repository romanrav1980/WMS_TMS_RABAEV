from pathlib import Path
root=Path("api/wms_api_server/app/modules/inventory")
p=root/"contracts_interwarehouse.py"
s=p.read_text(encoding="utf-8");s=s.replace("    def plan(self,", "    def record_decision(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...\n    def plan(self,",1);p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse.py";s=p.read_text(encoding="utf-8");s=s.replace("    def plan(self,","    def record_decision(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:\n        from .interwarehouse_dispatch import InterwarehouseDispatch\n        return InterwarehouseDispatch(self.gateway).record(operation_id,metadata,actor)\n\n    def plan(self,",1);p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse_onward.py";s=p.read_text(encoding="utf-8").replace("p.TARGET_TT_ID,p.OUTBOUND_DOCK from","RRL_INTERWARE_ROUTING.target_trip(p.OPERATION_ID),RRL_INTERWARE_ROUTING.outbound_dock(p.OPERATION_ID) from");p.write_text(s,encoding="utf-8")
p=root/"api/interwarehouse_routes.py";s=p.read_text(encoding="utf-8").replace("from typing import Any","from typing import Any, Literal")
s+='''

class DispatchDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    plan_operation_id: str = Field(strict=True,min_length=1,max_length=100)
    decision_kind: Literal["WAIT","DEFER"]
    expected_revision: int = Field(strict=True,ge=0)
    expected_arrival: datetime
    target_trip_id: int | None = Field(default=None,strict=True,gt=0)
    ready_due: datetime | None = None
    reason: str = Field(strict=True,min_length=1,max_length=500)
    decision_reference: str = Field(strict=True,min_length=1,max_length=60)

    @model_validator(mode="after")
    def decision_contract(self) -> "DispatchDecision":
        if self.expected_arrival.utcoffset() is None:
            raise ValueError("Timezone-aware expected arrival required")
        if self.decision_kind == "WAIT":
            if self.target_trip_id is not None or self.ready_due is not None:
                raise ValueError("WAIT preserves the current trip and deadline")
        elif self.target_trip_id is None or self.ready_due is None or self.ready_due.utcoffset() is None or self.ready_due < self.expected_arrival:
            raise ValueError("DEFER requires existing trip and aware ready deadline after expected arrival")
        if not self.reason.strip() or not self.decision_reference.strip():
            raise ValueError("Reason and decision reference required")
        return self

@router.post("/decisions")
def dispatch_decision(body: DispatchDecision,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.record_decision(body.operation_id,body.model_dump(exclude={"operation_id"},exclude_none=True),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc
'''
p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse_queue.sql";s=p.read_text(encoding="utf-8").replace("p.TARGET_WARE_ID,p.TARGET_TT_ID","p.TARGET_WARE_ID,coalesce(d.TARGET_TT_ID,p.TARGET_TT_ID) TARGET_TT_ID").replace("p.INBOUND_DOCK,p.OUTBOUND_DOCK","p.INBOUND_DOCK,coalesce(d.OUTBOUND_DOCK,p.OUTBOUND_DOCK) OUTBOUND_DOCK").replace("to_char(p.READY_DUE,","to_char(coalesce(d.READY_DUE,p.READY_DUE),")
s=s.replace("p.DECISION_REFERENCE,p.ACTOR,","p.DECISION_REFERENCE,p.ACTOR,\n p.TARGET_TT_ID ORIGINAL_TARGET_TRIP_ID,to_char(p.READY_DUE,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') ORIGINAL_READY_DUE,\n coalesce(d.REVISION_NO,0) DECISION_REVISION,d.DECISION_KIND,\n to_char(d.EXPECTED_ARRIVAL,'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') EXPECTED_ARRIVAL,d.DECISION_REFERENCE LATEST_DECISION_REFERENCE,")
s=s.replace("join RRL_TRANSPORT_TASK t","left join RRL_INTERWARE_DECISION d on d.PLAN_OPERATION_ID=p.OPERATION_ID and d.REVISION_NO=(select max(z.REVISION_NO)from RRL_INTERWARE_DECISION z where z.PLAN_OPERATION_ID=p.OPERATION_ID)\njoin RRL_TRANSPORT_TASK t",1);p.write_text(s,encoding="utf-8")
