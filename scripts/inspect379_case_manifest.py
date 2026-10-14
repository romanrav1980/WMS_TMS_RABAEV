exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context376.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COMPOSITION_JSON from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=ctx["load_operation_id"]);tree=read_oracle_json(q.fetchone()[0]);print(json.dumps({"root":tree["root"],"count":tree["physical_unit_count"],"nodes":tree["nodes"]},default=str))
 q.execute("select RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=ctx["load_operation_id"]);plan=read_oracle_json(q.fetchone()[0]);print(json.dumps(plan.get("physical_before"),default=str))
 q.execute("select CURRENT_UID,STOCK_STATUS,count(*)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:sscc group by CURRENT_UID,STOCK_STATUS",sscc=ctx.get("source_pallet",json.loads(Path("tmp/progress376.json").read_text())["sscc"]));print(q.fetchall())
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORE_MARK_CORE'and TYPE='PACKAGE BODY'order by LINE");Path("tmp/379_before_store.sql").write_text("create or replace "+"".join(x[0]for x in q).replace("\r","")+"\n/\n",encoding="utf-8")
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_INTERWARE_UNIT_SOURCE'and TYPE='PACKAGE BODY'order by LINE");Path("tmp/379_before_units.sql").write_text("create or replace "+"".join(x[0]for x in q).replace("\r","")+"\n/\n",encoding="utf-8")
