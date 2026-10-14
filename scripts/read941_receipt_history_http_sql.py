exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
ctx=json.loads(Path("tmp/context908.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
with httpx.Client(auth=("admin",password),base_url="http://127.0.0.1:8088",timeout=20)as client:
 path="/api/integrations/sap/supply-orders/"+ctx["order_id"]+"/receipt-history"
 response=client.get(path,params={"limit":1});assert response.status_code==200,response.text
 data=response.json();assert data["consistent_snapshot"]and data["source"]["receipt_state"]=="REVERSED"
 assert data["receipts"][0]["accepted_quantity"]=="3"and data["receipts"][0]["current_warehouse_quantity"]=="0"
 assert client.get(path,params={"limit":101}).status_code==422
 assert client.get(path,params={"after_operation":"UNKNOWN941"}).status_code==409
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,180)from V$SQL
 where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and upper(SQL_TEXT)like 'SELECT R.OPERATION_ID,R.LINE_NUMBER,R.UID_PALLET PALLET_IDENTIFIER%'
 order by LAST_ACTIVE_TIME desc fetch first 3 rows only""")
 queries=q.fetchall()
Path("tmp/history941.json").write_text(json.dumps({"http":data,"limit101_rejected":True,"foreign_cursor_rejected":True,"queries":queries,"decision":"Retain order/line receipt index and bounded100 keyset; per-pallet stock read restricted to source warehouse, no global stock inference or new stock index."},indent=2,default=str),encoding="utf-8")
print("941 HTTP PASS original3/currentwarehouse0/reversed coherent; limit101422 and unknowncursor409; SQL",json.dumps(queries))
