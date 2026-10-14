from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("from pydantic import BaseModel, Field","from pydantic import BaseModel, ConfigDict, Field")
s=s.replace("def status(self, identifier: str) -> dict: ...","def status(self, identifier: str, actor: str|None=None) -> dict: ...")
s=s.replace("    def check(self, identifier: str, body: dict, actor: str) -> dict: ...","    def check(self, identifier: str, body: dict, actor: str) -> dict: ...\n    def check_final(self, identifier: str, body: dict, actor: str) -> dict: ...")
s=s.replace("_user: AdminUser = Depends(require_permission","user: AdminUser = Depends(require_permission")
s=s.replace("return service.status(identifier)","return service.status(identifier,user.username)")
s+="""

class FinalWeightRequest(QualityRequest):
    model_config=ConfigDict(extra="forbid")
    capture_key: str = Field(pattern=r"^[A-F0-9]{64}$")

@router.post("/{identifier}/final-weight")
def final_weight(body:FinalWeightRequest,identifier:str=Path(min_length=1,max_length=150),
                 user:AdminUser=Depends(require_permission("outgoing_pallet_check")),
                 service:QualityPort=Depends(outgoing_quality_service))->dict:
    return service.check_final(identifier,body.model_dump(mode="json",exclude_none=True),user.username)
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..contracts_stock import StockCommand","from ..contracts_stock import StockCommand,StockPostingError\nfrom ...platform.public import read_oracle_json")
s=s.replace("def status(self, identifier: str) -> dict:","def status(self, identifier: str, actor: str|None=None) -> dict:")
needle="        try:\n            rows = self.gateway.fetch_all("
s=s.replace(needle,"""        try:
            if actor is not None:
                with self.gateway.transaction("Current warehouse QC status access")as q:
                    q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
            rows = self.gateway.fetch_all(""",1)
needle='            if getattr(exc.args[0],"code",None)==1403:'
s=s.replace(needle,'            if getattr(exc.args[0],"code",None)==20882:raise StockPostingError("OUTGOING_QC_FORBIDDEN","",20882)from exc\n'+needle,1)
s+="""

    def check_final(self,identifier:str,body:dict,actor:str)->dict:
        try:
            with self.gateway.transaction("Immutable whole CASE final scale source")as q:
                q.execute("set transaction read only")
                q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
                q.execute("select RESULT_JSON from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:p_key and CAPTURE_PURPOSE='FINAL_GROSS'",p_key=body["capture_key"])
                row=q.fetchone()
                if row is None:raise StockPostingError("FINAL_SCALE_CAPTURE_NOT_FOUND",body["operation_id"],20886)
                original=read_oracle_json(row[0])
        except oracledb.DatabaseError as exc:
            error=exc.args[0]
            raise StockPostingError("FINAL_SCALE_READ_REJECTED"if 20800<=error.code<=20899 else"RESULT_UNCERTAIN",body["operation_id"],error.code,str(error).split("\\n")[0])from exc
        metadata={key:value for key,value in body.items()if key!="capture_key"}
        metadata.update(quality_kind="WEIGHT",gross_weight=original["weight_kg"],wood_weight=original["tare_weight_kg"],final_scale_capture=body["capture_key"])
        return self.check(identifier,metadata,actor)
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py");s=p.read_text(encoding="utf-8")
old='q.execute("select RESULT_JSON from RRL_WH_SCALE_CAPTURE where CASE_PICK_TASK_ID=:task and CAPTURE_PURPOSE in(\'EMPTY_TARE\',\'FINAL_GROSS\') order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only",task=task)'
new="""q.execute("select c.RESULT_JSON,c.CAPTURE_KEY,u.STOCK_OPERATION_ID from(select RESULT_JSON,CAPTURE_KEY,RECEIVED_AT from RRL_WH_SCALE_CAPTURE where CASE_PICK_TASK_ID=:task and CAPTURE_PURPOSE in('EMPTY_TARE','FINAL_GROSS') order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only)c left join RRL_WH_FINAL_SCALE_USE u on u.CAPTURE_KEY=c.CAPTURE_KEY order by c.RECEIVED_AT desc,c.CAPTURE_KEY desc",task=task)"""
assert old in s;s=s.replace(old,new)
s=s.replace('return {"items":[read_oracle_json(row[0])for row in rows[:50]],"has_older":len(rows)>50}','return {"items":[read_oracle_json(row[0])for row in rows[:50]],"has_older":len(rows)>50,"use_by_capture":{row[1]:{"operation_id":row[2]}for row in rows[:50]if row[2]is not None}}')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
