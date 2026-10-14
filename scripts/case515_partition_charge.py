exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from concurrent.futures import ThreadPoolExecutor
src=json.loads(Path("tmp/context514.json").read_text(encoding="utf-8"))
p=Path("tmp/context515.json");ctx=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
ware=src["warehouse"];trip=src["trip"];svc=LogisticsCosts(OracleGateway())
def save():p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
if "policy"not in ctx:
 ctx["policy"]=svc.configure_period("POLICY515:"+str(ware),ware,"CASE_ASSEMBLY","UTC",0,"Own515 actual CASE date source","DEV515.UTC","admin");save()
preview=svc.assembly_period(trip,ware,"UTC","admin")
day=preview["business_dates"][0]
if "rate"not in ctx:
 ctx["rate"]=svc.rate(ware,"GEL","2.75",day,0,"Own515 dated recognition","DEV515.RATE","admin");save()
ops=["COST515.A:"+str(trip),"COST515.B:"+str(trip)]
def conduct(op):
 try:return ("ok",svc.calculate(op,trip,ware,"GEL","admin"))
 except Exception as e:return("error",getattr(e,"code",repr(e)))
if "result"not in ctx:
 with ThreadPoolExecutor(max_workers=2)as pool:rs=list(pool.map(conduct,ops))
 good=[r for state,r in rs if state=="ok"];bad=[r for state,r in rs if state=="error"]
 assert len(good)==1 and bad==["COST_ALREADY_CHARGED"],rs
 ctx["result"]=good[0];ctx["concurrent"]=rs;save()
r=ctx["result"]
assert r["amount"]=="2.75"and len(r["lines"])==1 and r["lines"][0]["rate_date"]==day,r
assert svc.calculate(r["operation_id"],trip,ware,"GEL","admin")==r
rows=svc.trip(trip,"admin")
assert rows["summary"]["currency_totals"]==[dict(currency="GEL",original_amount="2.75")]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select count(*),min(OPERATION_ID)from RRL_LOG_COST_SOURCE_CLAIM where LOAD_OPERATION_ID=:op",op=src["load_operation_id"])
 assert q.fetchone()==(1,r["operation_id"])
 q.execute("select count(*),min(PERIOD_KEY),sum(AMOUNT)from RRL_LOGISTICS_COST_LINE where LOAD_OPERATION_ID=:op",op=src["load_operation_id"])
 assert q.fetchone()==(1,day,2.75)
 q.execute("select count(*),sum(AMOUNT)from RRL_LOGISTICS_COST_LINE where PERIOD_KEY='LEGACY'");assert q.fetchone()==(5,13.5)
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'");assert q.fetchall()==[]
 q.execute("select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert q.fetchall()==[]
print("PASS515 actual CASE7/14 codes dated BOX1 charge2.75; competing operation one winner/source claim; exact replay; legacy5 lines/13.50 unchanged; native VALID.")
