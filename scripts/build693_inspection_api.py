import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/contracts_day_reviews.py");s=p.read_text(encoding="utf-8");s=s.replace("class DayReviewsPort(Protocol):","class DayReviewsPort(Protocol):\n    def inspection(self,review: str,actor: str) -> dict: ...\n    def inspect(self,operation: str,body: dict,actor: str) -> dict: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py");s=p.read_text(encoding="utf-8");anchor="    def shipping_register(";position=s.index(anchor)
s=s[:position]+"""    def inspection(self,review: str,actor: str) -> dict:
        from .day_inspections import DayInspections
        return DayInspections(self.gateway).get(review,actor)

    def inspect(self,operation: str,body: dict,actor: str) -> dict:
        from .day_inspections import DayInspections
        return DayInspections(self.gateway).record(operation,body,actor)

"""+s[position:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/finance/api/day_review_routes.py");s=p.read_text(encoding="utf-8").replace("from datetime import date","from datetime import date\nfrom typing import Literal")
s+="""

class InspectionBody(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    review_operation_id: str=Field(min_length=1,max_length=100)
    source_hash: str=Field(pattern=r"^[a-f0-9]{64}$")
    inspection_role: Literal["WAREHOUSE_CHIEF","DISPATCHER"]
    observed_empty: bool=Field(strict=True)
    note: str=Field(min_length=8,max_length=500)


@router.get("/reviews/{review_id}/shipping-inspections")
def inspection(review_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
               service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.inspection(review_id,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc


@router.post("/shipping-inspections",status_code=201)
def inspect(body: InspectionBody,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: DayReviewsPort=Depends(day_reviews_service)) -> dict:
    try:return service.inspect(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id})from exc
"""
out[str(p)]=s
root="db/migrations/2026-10-12_ni072_shipping_inspection/"
out.update({root+"003_ledger.sql":"""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-692-shipping-zone-inspection'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Independent warehouse chief and dispatcher declarations against immutable captured review; no day or quantity closure',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",root+"apply.sql":"@001_schema.sql\n@002_api.sql\n@003_ledger.sql\n",
root+"rollback.sql":"""declare n number;begin
 select count(*)into n from RRL_DAY_INSPECTION;
 if n!=0 then raise_application_error(-20886,'DAY_INSPECTION_HISTORY_PREVENTS_ROLLBACK');end if;
 execute immediate 'drop trigger RRL_DAY_INSPECT_GUARD';
 execute immediate 'drop package RRL_DAY_INSPECT_API';
 execute immediate 'drop table RRL_DAY_INSPECTION';
 delete from RIGHTS where ID='warehouse_day_inspection_confirm'and USER_GROUP='GLOBAL_ADMIN';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-692-shipping-zone-inspection';
end;
/
""",root+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_DAY_INSPECT_API','RRL_DAY_INSPECT_GUARD');\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_DAY_INSPECT_API','RRL_DAY_INSPECT_GUARD');\n"})
print(json.dumps(out))
