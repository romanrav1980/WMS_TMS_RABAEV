exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
result={};ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"));facts=json.loads(Path("tmp/result1313.json").read_text(encoding="utf-8"))["facts"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'");actor,password=q.fetchone()
 q.execute("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA in(:a,:b)",a="B01.1238:c0c2a00c0b:1",b="B01.1238:c0c2a00c0b:2");result["stock"]=q.fetchall();assert all(r[2]==0 and r[3]==0 for r in result["stock"])
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'");result["invalid"]=q.fetchall();assert not result["invalid"]
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,200)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%RRL_STORE_UNLOAD_CORE%'or SQL_TEXT like '%RRL_TT_LOAD_FLOOR_FACT%'or SQL_TEXT like '%Driver day%'or SQL_TEXT like '%RRL_TRANSPORT_DRIVER_USER%')order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 8 rows only""");result["sql"]=q.fetchall()
with httpx.Client(base_url="http://127.0.0.1:8088",auth=(actor,password),timeout=20)as client:
 result["replays"]=[]
 for fact in facts:
  if fact["kind"]!="receipt":continue
  r=client.post("/api/delivery/store-receipts/confirm",json=fact["request"]);r.raise_for_status();body=r.json()
  assert body==fact["body"],body
  result["replays"].append({"operation_id":body["operation_id"],"outbox":body["outbox_id"],"stock_consumed_again":body["warehouse_stock_consumed_again"]})
 result["reads"]=[]
 for url in ["/api/customer-orders/2135/delivery","/api/admin/slow-sql?limit=5&min_elapsed_ms=500"]:
  start=time.perf_counter();r=client.get(url);r.raise_for_status();result["reads"].append({"url":url,"ms":round((time.perf_counter()-start)*1000,2),"body":r.json()})
Path("tmp/verify1322.json").write_text(json.dumps(result,default=str,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items()if k!="reads"},default=str));print(json.dumps(result["reads"][0],default=str))
ctx["stage"]="B03_STORE_RECEIVED";ctx["store_receipts"]=facts;Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
