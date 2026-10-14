exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import httpx
ctx=json.loads(Path("tmp/context671.json").read_text(encoding="utf-8"))
with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
 body=dict(operation_id=ctx["group_store_operation_id"],load_operation_id=ctx["group_second_load_operation_id"],store_address=ctx["group_onward"]["members"][0]["final_address"],**ctx["group_store_metadata"])
 r=client.post("http://127.0.0.1:8088/api/delivery/store-receipts/confirm",json=body);assert r.status_code==409,r.text
 assert r.json()["detail"]["message"]=="OPERATION_CONFLICT"
 r=client.get("http://127.0.0.1:8088/api/inventory/interwarehouse/group-plans/"+ctx["group_plan_operation_id"]);assert r.status_code==200,r.text
 assert r.json()["delivered"]and r.json()["accepted_members"]==2
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where sql_text like '%RRL_WMS_RECEIPT_CODE CODE ON CODE.SYSTEM_CODE=SCAN_VALUE.S%'and executions>0 order by last_active_time desc fetch first 4 rows only");print("AGG_MODE_SQL",q.fetchall())
print("PASS720 different HTTP canonical defaults refused/current mixed group delivered2; native717 exact replay retained")
