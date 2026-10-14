exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
old=json.loads(Path("tmp/read1365.json").read_text(encoding="utf-8"))["HU1069:4bb85f1f15"]
proof=json.loads(Path("tmp/result1368.json").read_text(encoding="utf-8"));op=proof["writes"][0]["operation_id"];result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:op",op=op);result["goods_events"]=q.fetchone()[0];assert result["goods_events"]==0
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like 'select RRL_STOCK_HU_READ.snapshot_json%'or SQL_TEXT like 'select RRL_STOCK_HU_READ.case_snapshot_json%')order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 4 rows only""");result["sql"]=q.fetchall()
with httpx.Client(base_url="http://127.0.0.1:8088",auth=("admin",secret),timeout=20)as client:
 r=client.get("/api/warehouse-hus/composition",params={"identifier":old["root"]});r.raise_for_status();fresh=r.json();assert fresh["nodes"]==old["nodes"]and fresh["links"]==old["links"];result["same_nodes_links"]=True
print(json.dumps(result,default=str));Path("tmp/verify1369.json").write_text(json.dumps(result,default=str,indent=2),encoding="utf-8")
