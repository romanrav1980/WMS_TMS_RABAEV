exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context565.json").read_text(encoding="utf-8"));assert ctx["done"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_TT_HU_LOAD_ST","RRL_TT_HU_LOAD_FACT"]:
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:table_name order by COLUMN_ID",table_name=table);print(table,json.dumps(q.fetchall()))
 q.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=ctx["load"]);d=read_oracle_json(q.fetchone()[0])
 print("LOAD_RESULT_KEYS",list(d));print("SHIPMENT_KEYS",[list(r)for r in d.get("shipments",[])][:2])
