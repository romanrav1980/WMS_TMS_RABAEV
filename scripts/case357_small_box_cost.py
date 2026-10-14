exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.modules.finance.contracts import LogisticsCostError
from app.oracle_gateway import OracleGateway
op,trip,ware,box=json.loads(Path("tmp/356_box_candidates.json").read_text(encoding="utf-8"))[0]
service=LogisticsCosts(OracleGateway());path=Path("tmp/context357.json");saved=json.loads(path.read_text(encoding="utf-8"))if path.exists()else{}
def save():path.write_text(json.dumps(saved,indent=2),encoding="utf-8")
if "rate"not in saved:saved["rate"]=service.monthly_rate(ware,"GEL","2026-10","2","800","1600",0,"Own357 actual archived measured smallCASE norm","DEV357:SMALLBOX","admin");save()
operation="COST357.SMALL:"+str(trip)
result=service.calculate(operation,trip,ware,"GEL","admin");assert result["amount"]=="2.50"and result["lines"][0]["quantity"]==1,result
saved.update(result=result,operation_id=operation,load_operation_id=op,warehouse=ware,trip=trip,box=box);save()
assert service.calculate(operation,trip,ware,"GEL","admin")==result
try:service.calculate(operation+":OTHER",trip,ware,"GEL","admin")
except LogisticsCostError as e:assert e.code=="COST_ALREADY_CHARGED",str(e)
else:raise AssertionError("Double warehouse BOX charge admitted")
rows=service.trip(trip,"admin")["lines"];row=next(x for x in rows if x["operation_id"]==operation);assert row["components"]["common_work_rate"]=="0.5",row
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*),sum(QUANTITY),sum(AMOUNT)from RRL_LOGISTICS_COST_LINE where LOAD_OPERATION_ID=:op",op=op);assert q.fetchone()==(1,1,2.5)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
saved["read"]=rows;save()
print("PASS357 actual archived measured CASEbox1 (.45/.1/.35)/marked7EA14codes -> existing BOX cost2.50/monthly common.5 includedonce/replay/secondcharge denied/read components/no stock")
