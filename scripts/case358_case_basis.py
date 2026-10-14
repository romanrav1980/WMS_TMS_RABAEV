exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.expense_manifest import actual_goods
ctx=json.loads(Path("tmp/context357.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 weight=actual_goods(q,ctx["trip"],ctx["warehouse"],"WEIGHT");quantity=actual_goods(q,ctx["trip"],ctx["warehouse"],"BASE_QUANTITY")
 assert len(weight)==1 and weight[0]["quantity"]==7 and str(weight[0]["basis_value"])=="0.35",weight
 assert quantity[0]["basis_value"]==7
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
Path("tmp/context358.json").write_text(json.dumps(dict(weight=weight,quantity=quantity),default=str,indent=2),encoding="utf-8")
print("PASS358 existing actual CASE archive stockqty7/known measurednet.35KG -> original expense basis; no inferred multicontent weight/no stock")
