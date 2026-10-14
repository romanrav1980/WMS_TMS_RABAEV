from pathlib import Path
root=Path("api/wms_api_server/app/modules/inventory")
p=root/"contracts_interwarehouse.py";s=p.read_text(encoding="utf-8").replace("    def incoming(self,","    def decisions(self, plan_id: str, actor: str, after_revision: int=0) -> dict[str, Any]: ...\n    def incoming(self,",1);p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse.py";s=p.read_text(encoding="utf-8").replace("    def incoming(self,","    def decisions(self, plan_id: str, actor: str, after_revision: int=0) -> dict[str, Any]:\n        from .interwarehouse_decisions import InterwarehouseDecisions\n        return InterwarehouseDecisions(self.gateway).read(plan_id,actor,after_revision)\n\n    def incoming(self,",1);p.write_text(s,encoding="utf-8")
p=root/"api/interwarehouse_routes.py";s=p.read_text(encoding="utf-8").replace('    @model_validator(mode="after")\n    def decision_contract','''    incident_kind: Literal["TRANSPORT_DELAY","MISSING_PALLET","IDENTIFIER_MISMATCH"] | None = None
    incident_detail: str | None = Field(default=None,strict=True,min_length=1,max_length=1000)
    evidence_reference: str | None = Field(default=None,strict=True,min_length=1,max_length=200)

    @model_validator(mode="after")
    def decision_contract''',1)
s=s.replace('        if self.expected_arrival.utcoffset() is None:','''        if self.incident_kind is None and (self.incident_detail is not None or self.evidence_reference is not None) or self.incident_kind is not None and (not self.incident_detail or not self.incident_detail.strip() or not self.evidence_reference or not self.evidence_reference.strip()):
            raise ValueError("Incident kind, detail and evidence reference required together")
        if self.expected_arrival.utcoffset() is None:''',1)
s+='''
@router.get("/plans/{plan_id}/decisions")
def decisions(plan_id: str,after_revision: int=Query(default=0,ge=0,le=9999999999),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.decisions(plan_id,user.username,after_revision)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
'''
p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse_queue.sql";s=p.read_text(encoding="utf-8").replace("d.DECISION_REFERENCE LATEST_DECISION_REFERENCE,","d.DECISION_REFERENCE LATEST_DECISION_REFERENCE,incident.INCIDENT_KIND,incident.INCIDENT_DETAIL,incident.EVIDENCE_REFERENCE,incident.OPERATION_ID INCIDENT_OPERATION_ID,",1)
s=s.replace("join RRL_TRANSPORT_TASK t","left join RRL_INTERWARE_DECISION incident on incident.PLAN_OPERATION_ID=p.OPERATION_ID and incident.REVISION_NO=(select max(z.REVISION_NO)from RRL_INTERWARE_DECISION z where z.PLAN_OPERATION_ID=p.OPERATION_ID and z.INCIDENT_KIND is not null)\njoin RRL_TRANSPORT_TASK t",1);p.write_text(s,encoding="utf-8")
p=Path("wiki/database/nicora_ni061_incident_design_20261011.md");s=p.read_text(encoding="utf-8").replace(", повреждение","");p.write_text(s,encoding="utf-8")
