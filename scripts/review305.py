exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse_shortage import read_shortage
from app.modules.delivery.infrastructure.order_delivery import OrderDelivery
from app.oracle_gateway import OracleGateway
gw=OracleGateway();ctx=json.loads(Path("tmp/context305.json").read_text(encoding="utf-8"));saved=json.loads(Path("tmp/context305_recovery.json").read_text(encoding="utf-8"))
for part in saved["parts"]:
 view=read_shortage(gw,ctx["receipt_operation"],"admin",part["report_operation_id"])
 assert len(view["recovery_cases"])==2 and view["recovery_selection_quantity"]=="1"and view["recovered_quantity"]=="2"and view["net_unrecovered_short_quantity"]=="0"and view["unreported_recovery_quantity"]=="0"
 assert view["recovery_receipt_operation_id"]==part["receipt_operation_id"]and not view["current_unit_state_conflicts"]
try:read_shortage(gw,ctx["receipt_operation"],"admin","foreign-recovery-request")
except Exception as exc:assert getattr(exc,"status",None)==404,exc
else:raise AssertionError("crossreceiptselectionallowed")
for number in [291,292]:
 order=json.loads(Path("tmp/context303_"+str(number)+".json").read_text(encoding="utf-8"))["order_id"];assert OrderDelivery(gw).get(order)["quantities"][0]["accepted"]=="3"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,110)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and SQL_TEXT not like '%OPT_DYN_SAMP%'
 and SQL_TEXT not like 'CREATE %'and SQL_TEXT not like 'create %'and SQL_TEXT not like 'declare %'and SQL_TEXT not like '%USER_TABLES%'
 and(dbms_lob.instr(SQL_FULLTEXT,'INTERWARE_RECOVERY_REQUEST CLAIMED')>0 or SQL_TEXT like '%REQUEST_QUANTITY,req.SOURCE_JSON%')
 order by ELAPSED_TIME desc fetch first 4 rows only""");result=q.fetchall();print(json.dumps(result));Path("tmp/slow305.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print("PASS305 selectedrecovery current scoped read/globalfound2/net0/twocases/foreignselected404/oldbuyer3preserved")
