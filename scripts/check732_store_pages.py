exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.delivery_composition import build_delivery_receipt
from app.modules.delivery.contracts import StoreReceiptError
ctx=json.loads(Path("tmp/context671.json").read_text(encoding="utf-8"));service=build_delivery_receipt();trip=ctx["group_plan"]["target_trip_id"];address=ctx["group_onward"]["members"][0]["final_address"]
rows=service.places(trip,address,"admin",limit=1);assert len(rows)==1 and rows[0]["load_operation_id"]==ctx["group_second_load_operation_id"]
assert service.places(trip,address,"admin",after=rows[0]["load_operation_id"],limit=1)==[]
for after,limit in[(ctx["load_operation_id"],1),("",0),("",201)]:
 try:service.places(trip,address,"admin",after,limit)
 except StoreReceiptError as e:assert e.status==422
 else:raise AssertionError("Invalid scope/bound accepted")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where sql_text like 'with eligible as(%'and sql_text like '%RRL_TT_HU_LOAD_FACT%'and executions>0 order by last_active_time desc fetch first 3 rows only");print("SQL",q.fetchall())
print("PASS732 original trip/address/current receiver first page/empty continuation/foreign cursor/limit bounds; same-timestamp multiple places not exercised")
