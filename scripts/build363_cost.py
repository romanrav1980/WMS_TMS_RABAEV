from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/period_policy.py");t=p.read_text(encoding="utf-8")
t=t.replace('    cursor.execute("select VERSION_NO', '''    if lock:
        try:cursor.execute("insert into RRL_LOG_COST_PERIOD_HEAD(WARE_ID,VERSION_NO)select :ware,0 from dual where not exists(select 1 from RRL_LOG_COST_PERIOD_HEAD where WARE_ID=:ware)",ware=ware)
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0)!=1:raise
    cursor.execute("select VERSION_NO''',1)
t=t.replace('    if not row:return','    if not row or row[0]==0:return')
a=t.index('            if version==0:cursor.execute(');b=t.index('            result=',a)
t=t[:a]+'''            cursor.execute("update RRL_LOG_COST_PERIOD_HEAD set VERSION_NO=VERSION_NO+1 where WARE_ID=:ware and VERSION_NO=:version",ware=ware,version=version)
'''+t[b:];out[p.as_posix()]=t
p=Path("db/migrations/2026-10-12_ni071_period_policy/001_schema.sql");out[p.as_posix()]=p.read_text().replace('check(VERSION_NO>0)','check(VERSION_NO>=0)',1)
p=Path("api/wms_api_server/app/modules/finance/infrastructure/box_costs.py");t=p.read_text(encoding="utf-8");t=t.replace('from .cost_access import require_warehouse','from .cost_access import require_warehouse\nfrom .period_policy import current_policy')
t=t.replace('            cur.execute("""select l.LOAD_OPERATION_ID','            policy=current_policy(cur,ware,lock=True)\n            cur.execute("""select l.LOAD_OPERATION_ID',1)
marker='                cur.execute("""select h.RATE_KEY'
at=t.index(marker)
t=t[:at]+'''                if policy["period_mode"]=="CASE_ASSEMBLY":
                    case_ids=sorted({int(n["case_task_id"])for n in tree.get("nodes",[])if n.get("kind")=="CASE"and n.get("case_task_id")is not None})
                    if len(case_ids)!=boxes or boxes>200:
                        raise LogisticsCostError("COST_ASSEMBLY_SOURCE_REQUIRED","Каждой коробке нужен собственный источник начала CASE")
                    binds={f"case{i}":value for i,value in enumerate(case_ids)}
                    binds.update(region=policy["timezone_region"],ware=ware)
                    cur.execute("select CASE_PICK_TASK_ID,to_char(STARTED_AT_INSTANT at time zone(:region),'YYYY-MM-DD')from RRL_CASE_PICK_TASK where WARE_ID=:ware and CASE_PICK_TASK_ID in("+",".join(":case"+str(i)for i in range(len(case_ids)))+")",binds)
                    dates=cur.fetchall()
                    if len(dates)!=boxes or any(date is None for _,date in dates):
                        raise LogisticsCostError("COST_ACTUAL_ASSEMBLY_START_REQUIRED","Нет достоверного момента начала каждой коробки")
                    days={date for _,date in dates}
                    if len(days)!=1:
                        raise LogisticsCostError("COST_MULTIPLE_ASSEMBLY_PERIODS","В одном месте коробки разных расчётных дней; требуется отдельное распределение")
                    day=next(iter(days))
'''+t[at:]
t=t.replace('"На дату фактической погрузки нет ставки"','"На подтверждённую расчётную дату нет ставки"')
t=t.replace('"rate_date_utc":day','"rate_date_utc":day if policy["period_mode"]=="LOADED_UTC"else None,"rate_date":day,"period_mode":policy["period_mode"],"period_timezone":policy["timezone_region"],"period_policy_version":policy["version"]')
t=t.replace('AMOUNT,BASIS)values','AMOUNT,BASIS,RATE_DATE,PERIOD_MODE,PERIOD_TIME_ZONE,PERIOD_POLICY_VERSION)values')
t=t.replace(":amount,'BOX')",":amount,'BOX',to_date(:rate_date,'FXYYYY-MM-DD'),:period_mode,:period_zone,:period_version)")
t=t.replace('"amount":Decimal(line["amount"])}','"amount":Decimal(line["amount"]),"rate_date":line["rate_date"],"period_mode":line["period_mode"],"period_zone":line["period_timezone"],"period_version":line["period_policy_version"]}')
out[p.as_posix()]=t
for file in ["contracts.py","infrastructure/logistics_costs.py"]:
 p=Path("api/wms_api_server/app/modules/finance")/file;t=p.read_text(encoding="utf-8")
 at=t.index("    def rates(")
 methods='''    def period_policy(self,ware: int,actor: str) -> dict[str,Any]:
        from .period_policy import read_policy
        return read_policy(self.gateway,ware,actor)

    def configure_period(self,op: str,ware: int,mode: str,region: str|None,version: int,reason: str,reference: str,actor: str) -> dict[str,Any]:
        from .period_policy import set_policy
        return set_policy(self.gateway,op,ware,mode,region,version,reason,reference,actor)

'''
 if file=="contracts.py":methods='''    def period_policy(self,ware: int,actor: str) -> dict[str,Any]: ...
    def configure_period(self,op: str,ware: int,mode: str,region: str|None,version: int,reason: str,reference: str,actor: str) -> dict[str,Any]: ...
'''
 t=t[:at]+methods+t[at:];out[p.as_posix()]=t
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");t=p.read_text(encoding="utf-8");t+='''

class PeriodPolicy(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    period_mode: str=Field(strict=True,pattern=r"^(LOADED_UTC|CASE_ASSEMBLY)$")
    timezone_region: str|None=Field(default=None,strict=True,min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_/+:-]+$")
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

@router.get("/warehouses/{ware_id}/period-policy")
def period_policy(ware_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.period_policy(ware_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc

@router.post("/warehouses/{ware_id}/period-policy")
def configure_period(ware_id: int,body: PeriodPolicy,user: AdminUser=Depends(require_permission("create_tt_price")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.configure_period(body.operation_id,ware_id,body.period_mode,body.timezone_region,body.expected_version,body.reason,body.decision_reference,user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id)from exc
'''
out[p.as_posix()]=t
print(json.dumps(out))
