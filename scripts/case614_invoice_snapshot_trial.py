exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.finance.infrastructure.transport_cost_read import invoice_snapshot
d=json.loads(Path("tmp/context601.json").read_text(encoding="utf-8"));assert d["done"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select PAY_ORDER_ID,PRICE from RRL_TRANSPORT_TASK where ID=:id",id=d["trip"]);original=q.fetchone()
 q.execute("""select b.ID from RRL_BILL_ORDERS b where not exists(
  select 1 from RRL_TT_HU_LOAD_FACT l join RRL_TRANSPORT_TASK t on t.ID=l.TT_ID where t.PAY_ORDER_ID=b.ID)
  order by b.ID fetch first 1 rows only""")
 row=q.fetchone();assert row is not None,"Need an existing invoice without unrelated physical-load sources"
 invoice=int(row[0])
 try:
  q.execute("update RRL_TRANSPORT_TASK set PAY_ORDER_ID=:invoice where ID=:trip",invoice=invoice,trip=d["trip"])
  result=invoice_snapshot(q,invoice,"admin")
  assert len(result["items"])==1 and result["items"][0]["total"]=="107.25"and result["items"][0]["confirmed_total"]=="0"
  assert result["currency_totals"]==[{"currency":"GEL","amount":"107.25","confirmed_amount":"0"}]
  assert result["sources"]==[{"trip":d["trip"],"warehouse":d["warehouse"]}]
 finally:c.rollback()
 q.execute("select PAY_ORDER_ID,PRICE from RRL_TRANSPORT_TASK where ID=:id",id=d["trip"]);assert q.fetchone()==original
print("PASS614 same scoped invoice snapshot: original107.25/current0, grouped currency sums and original TT/LOAD source; temporary own trip invoice binding rolled back, carrier PRICE preserved.")
