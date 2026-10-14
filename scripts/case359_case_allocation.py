exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.logistics_expenses import LogisticsExpenses
from app.modules.finance.infrastructure.expense_allocation import ExpenseAllocation
from app.oracle_gateway import OracleGateway
ctx=json.loads(Path("tmp/context357.json").read_text(encoding="utf-8"));trip=ctx["trip"];ware=ctx["warehouse"];actor="QF359"+str(trip);path=Path("tmp/context359.json");saved=json.loads(path.read_text(encoding="utf-8"))if path.exists()else{}
def save():path.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME from RUSERS where ID=:id",id=actor);row=q.fetchone()
 if row is None:q.execute("insert into RUSERS(ID,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Own359 independent fixture logist','GLOBAL_ADMIN',:ware,0,0)",id=actor,ware=ware)
 else:
  assert row[0]=="Own359 independent fixture logist"
  q.execute("update RUSERS set DELETED=0 where ID=:id",id=actor)
 c.commit()
service=LogisticsExpenses(OracleGateway());allocate=ExpenseAllocation(OracleGateway());code="EX.CASE359:"+str(trip);expense="EX359.REPORT:"+str(trip)
try:
 if "article"not in saved:saved["article"]=service.article(code,"Own359 small CASE exceptional logistics","TRIP",False,True,0,"admin");save()
 if "report"not in saved:saved["report"]=service.report(expense,ware,code,"TRIP",trip,"2.01","GEL","2026-10-11","DEV359:CASE","Own359 independently reviewed additional trip expense",actor);save()
 if "logist"not in saved:saved["logist"]=service.decide("EX359.LOGIST:"+str(trip),expense,"LOGIST","APPROVE","WEIGHT","DEV359:L","Actual archived measured smallCASE source",actor);save()
 if "finance"not in saved:saved["finance"]=service.decide("EX359.FINANCE:"+str(trip),expense,"FINANCE","APPROVE","WEIGHT","DEV359:F","Separate fixture financial controller","admin");save()
 op="EX359.ALLOCATE:"+str(trip);result=allocate.allocate(op,expense,"admin");assert allocate.allocate(op,expense,"admin")==result
 assert len(result["lines"])==1 and result["lines"][0]["quantity"]=="7"and result["lines"][0]["weight_kg"]=="0.35"and result["lines"][0]["weight_source"]=="MEASURED_CASE_NET"and result["amount"]=="2.01",result
 saved.update(allocation=result,actor=actor,warehouse=ware,trip=trip);save()
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select count(*),sum(AMOUNT),sum(BASE_QTY),sum(WEIGHT_KG)from RRL_LOGISTICS_EXP_ALLOC_LINE where OPERATION_ID=:op",op=op);assert q.fetchone()==(1,2.01,7,0.35)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
finally:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  c.cursor().execute("update RUSERS set DELETED=1 where ID=:id and NAME='Own359 independent fixture logist'",id=actor);c.commit()
print("PASS359 original two-phase expense approval -> actual CASE stock7/net.35KG -> exact cents2.01 allocation/native source guard/replay/no stock; fixturelogist retired")
