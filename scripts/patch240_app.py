from pathlib import Path
root=Path("api/wms_api_server/app/modules/inventory")
p=root/"contracts_interwarehouse.py";s=p.read_text(encoding="utf-8").replace("    def record_decision(self,","    def record_temperature(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]: ...\n    def record_decision(self,",1);p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse.py";s=p.read_text(encoding="utf-8").replace("    def record_decision(self,","    def record_temperature(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:\n        from .interwarehouse_dispatch import InterwarehouseDispatch\n        return InterwarehouseDispatch(self.gateway).thermal(operation_id,metadata,actor)\n\n    def record_decision(self,",1);p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse_dispatch.py";s=p.read_text(encoding="utf-8").replace("        request = dict(metadata,operation_id=operation_id,actor=actor)","""        return self._record("RRL_INTERWARE_ROUTING.record_decision",operation_id,metadata,actor)

    def thermal(self, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        return self._record("RRL_INTERWARE_THERMAL.record_decision",operation_id,metadata,actor)

    def _record(self, procedure: str, operation_id: str, metadata: dict[str, Any], actor: str) -> dict[str, Any]:
        request = dict(metadata,operation_id=operation_id,actor=actor)""",1).replace('cur.callproc("RRL_INTERWARE_ROUTING.record_decision",[payload,actor,result])','cur.callproc(procedure,[payload,actor,result])')
p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse_onward.py";s=p.read_text(encoding="utf-8").replace("                ware,article,qty,unit,uid,source_st,source_load,target_trip,dock=source","""                ware,article,qty,unit,uid,source_st,source_load,target_trip,dock=source
                cur.execute("select PLAN_OPERATION_ID from RRL_INTERWARE_RECEIPT where OPERATION_ID=:receipt",receipt=receipt_id)
                cur.callproc("RRL_INTERWARE_THERMAL.assert_release",[cur.fetchone()[0]])""",1);p.write_text(s,encoding="utf-8")
p=root/"api/interwarehouse_routes.py";s=p.read_text(encoding="utf-8").replace("from datetime import datetime","from datetime import datetime\nfrom decimal import Decimal",1)
s+='''
class ThermalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    plan_operation_id: str = Field(strict=True,min_length=1,max_length=100)
    decision_kind: Literal["HOLD","PROCEED"]
    expected_revision: int = Field(strict=True,ge=0)
    observed_c: Decimal = Field(ge=-100,le=100,max_digits=6,decimal_places=3)
    observation_reference: str = Field(strict=True,min_length=1,max_length=200)
    task_temp_min: Decimal | None = Field(default=None,ge=-100,le=100,max_digits=6,decimal_places=3)
    task_temp_max: Decimal | None = Field(default=None,ge=-100,le=100,max_digits=6,decimal_places=3)
    reason: str = Field(strict=True,min_length=1,max_length=500)
    decision_reference: str = Field(strict=True,min_length=1,max_length=60)

    @model_validator(mode="after")
    def thermal_contract(self) -> "ThermalDecision":
        if (self.task_temp_min is None)!=(self.task_temp_max is None) or self.task_temp_min is not None and self.task_temp_min>self.task_temp_max:
            raise ValueError("Both ordered task temperature limits required")
        if not self.observation_reference.strip() or not self.reason.strip() or not self.decision_reference.strip():
            raise ValueError("Observation and decision references required")
        return self

@router.post("/temperature-decisions")
def temperature_decision(body: ThermalDecision,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.record_temperature(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"},exclude_none=True),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc
'''
p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse_queue.sql";s=p.read_text(encoding="utf-8").replace("p.TARGET_TT_ID ORIGINAL_TARGET_TRIP_ID,","coalesce(th.REVISION_NO,0) TEMPERATURE_REVISION,th.DECISION_KIND TEMPERATURE_DECISION,th.OBSERVED_C,th.TASK_TEMP_MIN,th.TASK_TEMP_MAX,th.OPERATION_ID TEMPERATURE_OPERATION_ID,\n p.TARGET_TT_ID ORIGINAL_TARGET_TRIP_ID,",1)
s=s.replace("join RRL_TRANSPORT_TASK t","left join RRL_INTERWARE_THERMAL_FACT th on th.PLAN_OPERATION_ID=p.OPERATION_ID and th.REVISION_NO=(select max(z.REVISION_NO)from RRL_INTERWARE_THERMAL_FACT z where z.PLAN_OPERATION_ID=p.OPERATION_ID)\njoin RRL_TRANSPORT_TASK t",1);p.write_text(s,encoding="utf-8")
