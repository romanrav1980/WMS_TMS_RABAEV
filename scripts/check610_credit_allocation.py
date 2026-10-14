exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.normative_correction import confirmed_total
d=json.loads(Path("tmp/context601.json").read_text(encoding="utf-8"))
assert d["done"]and d["allocation"]and d["rejected_stale"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select to_char(sum(l.AMOUNT*e.ADJUSTMENT_SIGN),'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')
 from RRL_LOGISTICS_EXP_ALLOC_LINE l join RRL_LOGISTICS_EXP_ALLOCATION a on a.OPERATION_ID=l.OPERATION_ID
 join RRL_LOGISTICS_EXPENSE e on e.OPERATION_ID=a.EXPENSE_OPERATION_ID where l.OPERATION_ID=:op""",op=d["allocation"]["operation_id"])
 assert q.fetchone()[0]=="-107.25"
 assert confirmed_total(q,d["cost_operation_id"])=="0"
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS610 existing allocation stores absolute cents + original expense sign: approved credit distributed exactly-107.25 once, stale proposal FINANCE rejected, confirmed0, protected stock20/20 unchanged.")
