exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.modules.finance.contracts import LogisticsCostError
from app.oracle_gateway import OracleGateway
svc=LogisticsCosts(OracleGateway());trip=33533;ware=35944973;path=Path("tmp/context364.json");ctx=json.loads(path.read_text())if path.exists()else{}
def save():path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
first=svc.configure_period("POLICY364.CASE:"+str(ware),ware,"CASE_ASSEMBLY","Asia/Tbilisi",0,"Own364 clock evidence gate","DEV364","admin");ctx["first"]=first;save()
assert svc.configure_period("POLICY364.CASE:"+str(ware),ware,"CASE_ASSEMBLY","Asia/Tbilisi",0,"Own364 clock evidence gate","DEV364","admin")==first
try:svc.calculate("COST364.MISSING:"+str(trip),trip,ware,"GEL","admin")
except LogisticsCostError as e:assert e.code=="COST_ACTUAL_ASSEMBLY_START_REQUIRED",e.code
else:raise AssertionError("Naive CASE charged as aware assembly")
try:svc.configure_period("POLICY364.CASE:"+str(ware),ware,"CASE_ASSEMBLY","Europe/Moscow",0,"Own364 clock evidence gate","DEV364","admin")
except LogisticsCostError as e:assert e.code=="COST_PERIOD_PAYLOAD_CONFLICT"
else:raise AssertionError("Same decision accepted different timezone")
if "second"not in ctx:
 ctx["second"]=svc.configure_period("POLICY364.LOAD:"+str(ware),ware,"LOADED_UTC",None,1,"Own364 preserve original loadedUTC explicit decision","DEV364.LOAD","admin");save()
assert svc.period_policy(ware,"admin")["version"]==2
if "rate"not in ctx:
 ctx["rate"]=svc.monthly_rate(ware,"GEL","2026-10","2","800","1600",0,"Own364 original departed smallCASE norm","DEV364.RATE","admin");save()
result=svc.calculate("COST364.LOAD:"+str(trip),trip,ware,"GEL","admin");ctx["result"]=result;save()
assert result["amount"]=="2.50"and result["lines"][0]["period_mode"]=="LOADED_UTC"and result["lines"][0]["period_policy_version"]==2
assert svc.calculate("COST364.LOAD:"+str(trip),trip,ware,"GEL","admin")==result
assert svc.configure_period("POLICY364.CASE:"+str(ware),ware,"CASE_ASSEMBLY","Asia/Tbilisi",0,"Own364 clock evidence gate","DEV364","admin")==first
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_LOGISTICS_COST_RUN where OPERATION_ID=:op",op="COST364.MISSING:"+str(trip));assert q.fetchone()[0]==0
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS364 explicitCASE timezone/version1/naive clock denied atomically/payload conflict/current loadedUTC v2/originalsmallCASE1BOX2.50/replay historicalpolicy/currentpolicy/protected20")
