exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.oracle_gateway import OracleGateway
tree=WarehouseHu(OracleGateway()).preview("HU994:4bb85f1f15","admin")
Path("tmp/read1052_nested_source.json").write_text(json.dumps(tree,indent=2,default=str),encoding="utf-8")
print(json.dumps(tree,ensure_ascii=True))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in("RRL_ST_DEFER_WAIT_PLAN","RRL_ST_DEFER_WAIT_RUN","RRL_WMS_HU_LINK"):
  q.execute("select COLUMN_NAME,DATA_TYPE,DATA_LENGTH from USER_TAB_COLUMNS where TABLE_NAME=:n order by COLUMN_ID",n=name)
  print(name,json.dumps(q.fetchall()))
 q.execute("select NAME,TYPE,TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_WAIT_PLAN_GUARD' order by LINE")
 Path("tmp/1052_wait_trigger.sql").write_text("".join(x[2] for x in q),encoding="utf-8")
