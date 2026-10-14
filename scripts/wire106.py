from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/tare_loss_routes.py");s=p.read_text(encoding="utf-8-sig").replace("ConfigDict,Field","ConfigDict,Field,model_validator",1)
s=s.replace('    expected_version: int=Field(strict=True,ge=1)','''    expected_version: int=Field(strict=True,ge=1)
    custodian_kind: Literal["WAREHOUSE","STORE","VEHICLE"]|None=None
    custodian_id: str|None=Field(default=None,strict=True,min_length=1,max_length=255)
    source_claim_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100)
    task_id: int|None=Field(default=None,strict=True,ge=1)
    scan_vehicle: str|None=Field(default=None,strict=True,min_length=1,max_length=50)

    @model_validator(mode="after")
    def source_required(self) -> "Report":
        if self.custodian_kind=="STORE" and(not self.custodian_id or not self.source_claim_id):raise ValueError("Store loss requires original claim and current store")
        if self.custodian_kind=="VEHICLE" and(not self.custodian_id or not self.task_id or not self.scan_vehicle):raise ValueError("Vehicle loss requires current trip/id/scan")
        if self.custodian_id and len(self.custodian_id.encode("utf-8"))>255:raise ValueError("Holder identifier exceeds255 bytes")
        return self''',1)
s=s.replace('    if isinstance(body,Decision):','''    if isinstance(body,Report):
        for key in ("source_claim_id","task_id"):
            value=metadata.pop(key,None)
            if value is not None:source[key]=value
        for key in ("custodian_kind","custodian_id","scan_vehicle"):
            if metadata.get(key) is None:metadata.pop(key,None)
    if isinstance(body,Decision):''',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py");s=p.read_text(encoding="utf-8-sig").replace("c.DECISION_REFERENCE,c.ACTOR,c.CREATED_AT,","c.DECISION_REFERENCE,c.ACTOR,c.CREATED_AT,b.CUSTODIAN_KIND,b.CUSTODIAN_ID,c.SOURCE_CLAIM_ID,c.TRANSPORT_TASK_ID,",1).replace("from RRL_TARE_LOSS_CLAIM c join RRL_PALLET_TYPE","from RRL_TARE_LOSS_CLAIM c join RRL_TARE_BALANCE b on b.BALANCE_KEY=c.BALANCE_KEY join RRL_PALLET_TYPE",1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
