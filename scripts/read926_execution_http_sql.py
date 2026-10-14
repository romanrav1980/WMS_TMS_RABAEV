exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import httpx
saved=json.loads(Path("tmp/order923.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
response=httpx.get("http://127.0.0.1:8088/api/customer-orders/"+str(saved["customer_order_id"])+"/execution",auth=("admin",password),timeout=20)
assert response.status_code==200,response.text
data=response.json()
print("926 HTTP",data.get("consistent_snapshot"),data.get("warehouse_id"),data["execution_status"],len(data["lines"]))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,180)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and upper(SQL_TEXT)like 'SELECT R.CUSTOMER_ORDER_ROW_ID,R.LINE_NO,R.ARTICUL,R.UNIT_CODE,R.STATUS ROW_STATUS%'
 order by LAST_ACTIVE_TIME desc fetch first 3 rows only""")
 queries=q.fetchall()
 print("926 SQL",json.dumps(queries))
Path("tmp/execution926.json").write_text(json.dumps({"http_current":data.get("consistent_snapshot")is True,"order":saved,"queries":queries,"decision":"Retain indexed order-bound physical provenance <=2000 lines; independent larger waves may require batching/plan check, not proved production scale."},indent=2,default=str),encoding="utf-8")
