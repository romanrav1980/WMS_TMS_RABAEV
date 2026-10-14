exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.schemas import WarehouseTaskStatusRequest
ctx=json.loads(Path("tmp/context994.json").read_text(encoding="utf-8"));source=json.loads(Path("tmp/context987.json").read_text(encoding="utf-8"));path=Path("tmp/context996.json")
assert not path.exists(),"996 exists; retained replay only"
record={"root":ctx["root"],"stage":"NEW"};path.write_text(json.dumps(record),encoding="utf-8")
hu=WarehouseHu(OracleGateway());tree=hu.preview(ctx["root"],"admin");caseid,line,carrier,qty,cell=source["cases"][0]
body={"child_case_task_id":caseid,"expected_version":int(tree["nodes"][0]["version"]),"expected_child_version":5,"scan_container":ctx["root"],"scan_child":carrier,"reason":"Own retained intact CASE detached for next warehouse operation"}
result=hu.command("HU_DETACH",ctx["root"],"HU996.DETACH:"+source["tag"],body,"admin");assert hu.command("HU_DETACH",ctx["root"],"HU996.DETACH:"+source["tag"],body,"admin")==result
record.update(result=result,body=body,stage="DETACHED")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(6,6,ctx["target"])
 q.execute("select count(*)from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=:id and ACTIVE_FLAG=1",id=caseid);assert q.fetchone()==(0,)
 q.execute("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:op",op="TARE987.BOOK:"+source["tag"]+":"+str(caseid));assert q.fetchone()==("HELD",)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:w",w=source["wave"]);assert q.fetchone()==(20,20)
 q.execute("select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where sql_text like 'SELECT%RRL_CUSTOMER_ORDER_FULFILLMENT%LEGACY_SBORKA_PALLET_ID%'and executions>0 order by last_active_time desc fetch first 4 rows only");record["sql"]=q.fetchall()
record["after_tree"]=hu.preview(ctx["root"],"admin");record["detached_case"]=hu.preview(carrier,"admin")
record["evidence"]={"case_version":6,"ff_version":6,"hard_total":"20","physical_total":"20","tare_original_booking":"HELD","link_removed":True,"exact_replay":True}
path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
print("PASS996 existingHU detach CASE/CT6FF6/old TARE bookingHELD/no link/qty20H20/exact replay")
