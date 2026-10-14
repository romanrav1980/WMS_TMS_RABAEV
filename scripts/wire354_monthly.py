from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/box_rates.py");s=p.read_text(encoding="utf-8");out["tmp/354_before_box_rates.py"]=s
s=s.replace("import oracledb","import json,oracledb\nfrom ...platform.public import read_oracle_json",1)
s=s.replace("actor: str) -> dict[str,Any]:","actor: str, *, components: dict[str,str] | None=None) -> dict[str,Any]:",1)
s=s.replace('    key=sha256',"""    def result() -> dict[str,Any]:
        value={"warehouse_id":ware,"cost_code":"WAREHOUSE_PICKING","currency":currency,"rate_key":key,"version":version+1,"rate":str(amount),"basis":"BOX","effective_from":effective,"common_work_included":True}
        if components is not None:value["components"]=components
        return value
    key=sha256""",1)
s=s.replace("DECISION_REFERENCE,ACTOR from RRL_LOGISTICS_RATE_HISTORY","DECISION_REFERENCE,ACTOR,COMPONENTS_JSON from RRL_LOGISTICS_RATE_HISTORY")
s=s.replace("prior[1:]==(effective,reason,reference,actor)","prior[1:5]==(effective,reason,reference,actor) and (read_oracle_json(prior[5])if prior[5]is not None else None)==components")
line='return {"warehouse_id":ware,"cost_code":"WAREHOUSE_PICKING","currency":currency,"rate_key":key,"version":version+1,"rate":str(amount),"basis":"BOX","effective_from":effective,"common_work_included":True}'
s=s.replace(line,"return result()")
s=s.replace('            cur.execute("insert into RRL_LOGISTICS_RATE_HISTORY(', '            cur.setinputsizes(components_body=oracledb.DB_TYPE_CLOB)\n            cur.execute("insert into RRL_LOGISTICS_RATE_HISTORY(',1)
s=s.replace("DECISION_REFERENCE,ACTOR)values(:key,:version,:value,to_date(:effective,'FXYYYY-MM-DD'),:reason,:reference,:actor)","DECISION_REFERENCE,ACTOR,COMPONENTS_JSON)values(:key,:version,:value,to_date(:effective,'FXYYYY-MM-DD'),:reason,:reference,:actor,:components_body)",1)
s=s.replace('"actor":actor})\n            return result()','"actor":actor,"components_body":json.dumps(components,sort_keys=True,separators=(",",":"))if components is not None else None})\n            return result()',1)
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/contracts.py");s=p.read_text(encoding="utf-8");s=s.replace("    def calculate(","    def monthly_rate(self,ware: int,currency: str,month: str,picking: str,common: str,boxes: str,version: int,reason: str,reference: str,actor: str) -> dict[str,Any]: ...\n    def calculate(",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");s=p.read_text(encoding="utf-8").replace("from .box_rates import set_box_rate","from .box_rates import set_box_rate\nfrom .monthly_rates import set_monthly_rate",1);s=s.replace("    def calculate(","    def monthly_rate(self,ware: int,currency: str,month: str,picking: str,common: str,boxes: str,version: int,reason: str,reference: str,actor: str) -> dict[str,Any]:\n        return set_monthly_rate(self.gateway,ware,currency,month,picking,common,boxes,version,reason,reference,actor)\n\n    def calculate(",1)
# Current read stays authorized in one snapshot and returns component provenance
start=s.index('        with self.gateway.transaction("Read current warehouse cost rate")')
end=s.index("\n    def trip(",start)
s=s[:start]+"""        from ...platform.public import read_oracle_json
        with self.gateway.transaction("Read current warehouse cost rate") as cur:
            cur.execute("set transaction read only")
            require_warehouse(cur,ware,actor,"transport_dispatch_view")
            cur.execute(\"\"\"select h.CURRENCY,h.VERSION_NO,to_char(r.RATE_VALUE,'TM9') RATE_VALUE,
            to_char(r.EFFECTIVE_FROM,'YYYY-MM-DD') EFFECTIVE_FROM,r.BASIS,r.REASON_TEXT,r.DECISION_REFERENCE,r.COMPONENTS_JSON
            from RRL_LOGISTICS_RATE_HEAD h join RRL_LOGISTICS_RATE_HISTORY r on r.RATE_KEY=h.RATE_KEY and r.VERSION_NO=h.VERSION_NO
            where h.WARE_ID=:ware order by h.CURRENCY fetch first 50 rows only\"\"\",ware=ware)
            columns=[x[0].lower()for x in cur.description]
            rows=[]
            for values in cur.fetchall():
                row=dict(zip(columns,values));wire=row.pop("components_json");row["components"]=read_oracle_json(wire)if wire is not None else None;rows.append(row)
            return rows
""" +s[end:];out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");s=p.read_text(encoding="utf-8");idx=s.index("class Calculate(")
s=s[:idx]+"""class MonthlyRate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    warehouse_id: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")
    month: str=Field(strict=True,pattern=r"^[0-9]{4}-[0-9]{2}$")
    picking_rate: str=Field(strict=True,min_length=1,max_length=40)
    common_work_amount: str=Field(strict=True,min_length=1,max_length=40)
    basis_boxes: str=Field(strict=True,pattern=r"^[0-9]{1,12}$")
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

"""+s[idx:]
idx=s.index('@router.get("/warehouses/')
s=s[:idx]+"""@router.post("/rates/monthly")
def monthly_rate(body: MonthlyRate,user: AdminUser=Depends(require_permission("create_tt_price")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.monthly_rate(body.warehouse_id,body.currency,body.month,body.picking_rate,body.common_work_amount,body.basis_boxes,body.expected_version,body.reason,body.decision_reference,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

"""+s[idx:];out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/domain/monthly_rate.py");s=p.read_text(encoding="utf-8")
s=s.replace('    return {"month":','    def canonical(value: Decimal) -> str:\n        return format(value.normalize(), "f")\n    return {"month":',1)
for v in["base","total","count","share","combined"]:s=s.replace('format('+v+', "f")','canonical('+v+')')
out[p.as_posix()]=s
print(json.dumps(out))
