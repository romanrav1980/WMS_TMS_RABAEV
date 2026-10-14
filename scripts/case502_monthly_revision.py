exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
from app.modules.finance.domain.cost_summary import recognized_cost_summary
import httpx
source=json.loads(Path("tmp/context499.json").read_text(encoding="utf-8"));ware=source["warehouse"];trip=source["trip"]
p=Path("tmp/context502.json");ctx=json.loads(p.read_text(encoding="utf-8"))if p.exists()else dict(source=source)
svc=LogisticsCosts(OracleGateway())
def save():p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
for version,common,key in [(0,"50","norm1"),(1,"100","norm2")]:
 if key not in ctx:
  ctx[key]=svc.monthly_rate(ware,"GEL","2026-10","2",common,"100",version,"Own502 same monthly period revision","DEV502."+key,"admin");save()
assert ctx["norm1"]["rate"]=="2.5"and ctx["norm2"]["rate"]=="3",(ctx["norm1"]["rate"],ctx["norm2"]["rate"])
op="COST502.MONTHLY:"+str(trip)
result=svc.calculate(op,trip,ware,"GEL","admin")
assert result["amount"]=="3.00"and result["lines"][0]["version"]==2,result
if "norm3"not in ctx:ctx["norm3"]=svc.monthly_rate(ware,"GEL","2026-10","2","200","100",2,"Own502 later revision preserves prior charge","DEV502.norm3","admin");save()
assert svc.calculate(op,trip,ware,"GEL","admin")==result
if "future"not in ctx:ctx["future"]=svc.rate(ware,"GEL","9","2026-11-01",3,"Own502 future revision","DEV502.future","admin");save()
assert svc.calculate(op,trip,ware,"GEL","admin")==result
rows=svc.trip(trip,"admin")["lines"];assert len(rows)==1 and rows[0]["version_no"]==2 and rows[0]["amount"]=="3",rows
summary=recognized_cost_summary(rows);assert summary["currency_totals"]==[dict(currency="GEL",original_amount="3.00")],summary
try:svc.calculate(op+".DUP",trip,ware,"GEL","admin")
except Exception as e:assert getattr(e,"code",None)=="COST_ALREADY_CHARGED",repr(e)
else:raise AssertionError("Duplicate charge admitted")
ctx.update(result=result,summary=summary);save()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=:ware",ware=ware);assert q.fetchone()==(0,0)
 q.execute("select count(*)from RRL_LOGISTICS_COST_LINE where LOAD_OPERATION_ID=:op",op=source["load_operation_id"]);assert q.fetchone()[0]==1
 q.execute("select ID from RRL_BILL_ORDERS order by ID desc fetch first 1 row only");invoice=q.fetchone()
 if invoice:
  with httpx.Client(auth=("admin","admin123"),timeout=35)as h:
   r=h.get(f"http://127.0.0.1:8088/api/finance/logistics-costs/billing-orders/{invoice[0]}/summary")
   assert r.status_code==200,r.text;assert r.json()["scope"]=="VISIBLE_WAREHOUSES",r.text
print("PASS502 same-month norm revisions1=2.5/2=3 ->actual measured CASE BOX1 charge3 frozenv2; v3=4/futurev4=9 preserve replay3; duplicate denied; real-source summary3GEL/HTTPinvoice contract/no stock")
