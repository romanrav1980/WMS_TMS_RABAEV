exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx,time
p=Path("tmp/context1238.json");ctx=json.loads(p.read_text(encoding="utf-8"));result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor()
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_ST_LAYOUT_READ','RRL_STOCK_ST_ROW_CMD','RRL_UPDATE_SBORKA_PALLET_ROWS2','RRL_STOCK_POSTING_API','RRL_PICKING_API')order by NAME,SEQUENCE");result["errors"]=q.fetchall();assert not result["errors"]
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'order by OBJECT_NAME,OBJECT_TYPE");result["invalid"]=q.fetchall();assert not result["invalid"]
 q.execute("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA in(:a,:b)order by UID_POLETA,CELL",a="B01.1238:"+ctx["tag"]+":1",b="B01.1238:"+ctx["tag"]+":2");result["stock"]=q.fetchall();assert all(row[2]==0 and row[3]==0 for row in result["stock"])
 q.execute("select FULFILLMENT_ID,STATUS,FACT_QTY,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=2135 order by FULFILLMENT_ID");result["fulfillment"]=q.fetchall();assert len(result["fulfillment"])==2 and all(row[1]=="SHIPPED"and row[2]==18 for row in result["fulfillment"])
 q.execute("select ID,PASS from RUSERS where ID='admin'");actor,password=q.fetchone()
 try:
  q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,220) from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%' and (SQL_TEXT like '%RRL_ST_LAYOUT_READ%' or SQL_TEXT like '%RRL_TT_HU_LOAD_ST%' or SQL_TEXT like '%RRL_CUSTOMER_ORDER_FULFILLMENT%') order by ELAPSED_TIME/nullif(EXECUTIONS,0) desc fetch first 8 rows only""")
  result["oracle_top"]=q.fetchall()
 except Exception as e:result["oracle_top_error"]=str(e)
with httpx.Client(auth=(actor,password),base_url="http://127.0.0.1:8088",timeout=20)as client:
 result["reads"]=[]
 for url in ["/api/customer-orders/2135/delivery","/api/picking/waves/559/execution","/api/transport/loading/33571/status","/api/admin/slow-sql?limit=8&min_elapsed_ms=500"]:
  start=time.perf_counter();r=client.get(url);result["reads"].append({"url":url,"status":r.status_code,"ms":round((time.perf_counter()-start)*1000,2),"body":r.json()});r.raise_for_status()
 r=client.post("/api/transport/loading/33571/depart",json=ctx["departure"]["request"]);r.raise_for_status();result["departure_replay"]=r.json();assert r.json()["operation_id"]==ctx["departure"]["request"]["operation_id"] and r.json()["stock_consumed_again"]is False
Path("tmp/verify1289.json").write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items()if k!="reads"},default=str))
print(json.dumps({"reads":[{k:v for k,v in x.items()if k!="body"}for x in result["reads"]]}))
