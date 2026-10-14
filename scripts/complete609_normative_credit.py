exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.expense_allocation import ExpenseAllocation
from app.modules.finance.infrastructure.logistics_expenses import LogisticsExpenses
from app.modules.finance.infrastructure.normative_correction import confirmed_total
from app.oracle_gateway import OracleGateway
p=Path("tmp/context601.json");d=json.loads(p.read_text(encoding="utf-8"));assert d["done"]
winner=next(row for row in d["results"]if "result"in row);loser=next(row for row in d["results"]if "error"in row)
if "allocation"in d:raise SystemExit("609 completed; exact saved replay only")
alloc=ExpenseAllocation(OracleGateway());expense=winner["body"]["expense"]
result=alloc.allocate("CORR609.ALLOC:"+d["tag"],expense,"admin")
assert alloc.allocate("CORR609.ALLOC:"+d["tag"],expense,"admin")==result
d["allocation"]=result;p.write_text(json.dumps(d,indent=2),encoding="utf-8")
svc=LogisticsExpenses(OracleGateway())
reject=svc.decide("CORR609.REJECT:"+d["tag"],loser["body"]["expense"],"FINANCE","REJECT","WEIGHT","DEV609:"+d["tag"],"Competing full credit became stale; original already credited","admin")
d["rejected_stale"]=reject;p.write_text(json.dumps(d,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();assert confirmed_total(q,d["cost_operation_id"])=="0"
 q.execute("select to_char(sum(AMOUNT*ADJUSTMENT_SIGN),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from RRL_LOGISTICS_EXP_ALLOC_LINE where OPERATION_ID=:op",op=result["operation_id"]);assert q.fetchone()[0]=="-107.25"
print("PASS609 original approved normative credit distributed through existing WEIGHT/cents allocator exactly-107.25 once; stale other credit independently rejected, adjusted total stays0; no goods writer.")
