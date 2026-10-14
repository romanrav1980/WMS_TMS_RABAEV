exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from time import perf_counter
ctx=json.loads(Path("tmp/context1238.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select OBJECT_NAME,PROCEDURE_NAME from USER_PROCEDURES where upper(OBJECT_NAME) like '%SBORKA%'or upper(PROCEDURE_NAME) like '%PALLET%' order by OBJECT_NAME,PROCEDURE_NAME fetch first 65 rows only");print(json.dumps({"legacy_writers":q.fetchall()}))
 from app.modules.inventory.infrastructure.placement import ReceiptPlacement
 payload=ctx["pending_receipt_body"]
 print(json.dumps({"receipt_keys":list(payload)}))
 started=perf_counter()
 try:
  selected=ReceiptPlacement(q).choose(9807,"CPT_9807",ctx["articles"][0],payload)
  print(json.dumps({"placement":selected,"elapsed_ms":round((perf_counter()-started)*1000,2)}))
 except Exception as e:print(json.dumps({"placement_error":str(e),"elapsed_ms":round((perf_counter()-started)*1000,2)}))
 q.execute("select CELL,UID_POLETA,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA in(:a,:b)order by UID_POLETA,CELL",a="B01.1238:"+ctx["tag"]+":1",b="B01.1238:"+ctx["tag"]+":2")
 print(json.dumps({"stock":q.fetchall()}))
