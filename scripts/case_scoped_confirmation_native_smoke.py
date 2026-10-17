"""Scoped CASE proof on reviewed shared DEV fixture: every quantity effect caller rollback.
No metadata staging, no hardware claim, no StockPosting.post.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.platform.public import read_oracle_json,stock_configuration_transaction
ACTOR="WHREQ15.OP";LOT="REUSE.RETURN:e6c16d0bbd";WARE=13583852
REPORT=ROOT/"reports/retailcase/2026-10-15/scoped-case-audit/native-acceptance.json"


def scalar(cursor,sql,**bind):
    cursor.execute(sql,bind);return cursor.fetchone()[0]


def post(cursor,command):
    output=cursor.var(oracledb.DB_TYPE_CLOB)
    cursor.callproc("RRL_STOCK_POSTING_API.prepare_command",[command.canonical_json(),command.actor,output])
    if output.getvalue()is None:cursor.callproc("RRL_STOCK_POSTING_API.execute_prepared",[output])
    return read_oracle_json(output.getvalue())


def snapshot(gateway,task,line):
    return dict(stock=gateway.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u order by CELL",{"u":LOT}),
        task=gateway.fetch_all("select STATUS,PICKED_QTY,CONTENT_VERSION,LEGACY_SBORKA_PALLET_ID,ASSIGNED_TO,ASSIGNED_RESOURCE_ID,RESOURCE_SESSION_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":task}),
        line=gateway.fetch_all("select STATUS,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:l",{"l":line}),
        case_events=gateway.fetch_all("select count(*) N from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:t",{"t":task}),
        resource_events=gateway.fetch_all("select count(*) N from RRL_RESOURCE_FACT_EVENT where TASK_ID=:t",{"t":task}))


class RollbackPhysicalTrial(Exception):pass


def physical_guards(gateway,ctx,task,checks):
    cases=[("update RRL_RESOURCE_TASK_QUAL set ACTIVE=0 where RESOURCE_ID=:id and TASK_TYPE='CASE_PICK'",ctx["resource_id"],"CASE_RESOURCE_QUALIFICATION_REQUIRED"),
           ("update RRL_RESOURCE_SHIFT set STATUS='PLANNED' where SHIFT_ID=:id",ctx["shift_id"],"CASE_SHIFT_UNAVAILABLE"),
           ("update RRL_RESOURCE_SESSION set STATUS='PAUSED' where SESSION_ID=:id",ctx["session_id"],"CASE_SESSION_UNAVAILABLE"),
           ("update RRL_RESOURCE set WARE_ID=6667491 where RESOURCE_ID=:id",ctx["resource_id"],"CASE_RESOURCE_UNAVAILABLE")]
    for sql,identity,expected in cases:
        try:
            with stock_configuration_transaction(gateway,"Shared TEST physical guard caller rollback","admin","warehouse_settings_edit")as cursor:
                cursor.execute(sql,{"id":identity});assert cursor.rowcount==1
                try:cursor.callfunc("RRL_CASE_RESOURCE_POLICY.context_json",oracledb.DB_TYPE_CLOB,[task,"COMPLETE",ACTOR,None,None,None])
                except oracledb.DatabaseError as error:assert expected in str(error),(expected,str(error))
                else:raise AssertionError(expected+" unexpectedly admitted")
                raise RollbackPhysicalTrial()
        except RollbackPhysicalTrial:pass
        checks.append(expected+"_rollback")
    assert gateway.fetch_all("select ACTIVE from RRL_RESOURCE_TASK_QUAL where RESOURCE_ID=:id and TASK_TYPE='CASE_PICK'",{"id":ctx["resource_id"]})==[{"active":1}]
    assert gateway.fetch_all("select STATUS from RRL_RESOURCE_SHIFT where SHIFT_ID=:id",{"id":ctx["shift_id"]})==[{"status":"OPEN"}]
    assert gateway.fetch_all("select STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:id",{"id":ctx["session_id"]})==[{"status":"ACTIVE"}]
    assert gateway.fetch_all("select WARE_ID from RRL_RESOURCE where RESOURCE_ID=:id",{"id":ctx["resource_id"]})==[{"ware_id":WARE}]


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--task",type=int,required=True);args=parser.parse_args()
    gateway=OracleGateway();ctx=json.loads((REPORT.parent/"shared-resources.json").read_text(encoding="utf-8"))
    assert ctx["task_id"]==args.task and ctx.get("native_only"),ctx
    lines=gateway.fetch_all("select CASE_PICK_LINE_ID,CELL_CODE,ARTICUL,PLANNED_QTY,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:t",{"t":args.task});assert len(lines)==1
    line=lines[0];line_id=line["case_pick_line_id"];assert line["planned_qty"]==1 and line["picked_qty"]==0,line
    container=gateway.fetch_all("select WARE_ID,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":args.task})[0];assert container["ware_id"]==WARE
    operation="WHREQ15.SCOPED.ROLLBACK"
    assert not gateway.fetch_all("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:o",{"o":operation})
    command=StockCommand(operation,"CASE_PICK_CONFIRM",ACTOR,(),{"case_task_id":args.task,"case_line_id":line_id},metadata={"fact_qty":"1","scan_cell":line["cell_code"],"scan_product":line["articul"],"scan_container":container["sscc"],"offline_event_id":None})
    before=snapshot(gateway,args.task,line_id);checks=[]
    assert sum(row["remain"]for row in before["stock"])==24 and sum(row["hard_reserved_base"]for row in before["stock"])==1,before
    assert [row["cell"]for row in before["stock"]if row["remain"]>0]==[line["cell_code"]],before
    physical_guards(gateway,ctx,args.task,checks)
    for denied_actor,denied_task,label in (("WHREQ15.GW",args.task,"dedicated_sender_has_no_operator_right"),(ACTOR,1031,"other_unassigned_case_not_granted_by_self")):
        denied=StockCommand(operation+".DENY", "CASE_PICK_CONFIRM",denied_actor,(),{"case_task_id":denied_task,"case_line_id":line_id},metadata=command.metadata)
        with oracle_connection()as connection:
            cursor=connection.cursor()
            try:
                try:post(cursor,denied)
                except oracledb.DatabaseError as error:assert error.args[0].code==20882,str(error)
                else:raise AssertionError(label+" unexpectedly admitted")
            finally:connection.rollback();cursor.callproc("RRL_STOCK_POSTING_API.reset_connection")
        assert not gateway.fetch_all("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:o",{"o":denied.operation_id})
        checks.append(label)
    with oracle_connection()as connection:
        cursor=connection.cursor()
        try:
            assert scalar(cursor,"select RRL_HAS_WRIGHT(:a,'case_pick_execute')from dual",a=ACTOR)==0
            assert scalar(cursor,"select RRL_CASE_TASK_ACCESS.has_current_scoped_execute(:t,:a)from dual",t=args.task,a=ACTOR)==1
            assert scalar(cursor,"select RRL_CASE_TASK_ACCESS.scoped_executor(:t,:a)from dual",t=args.task,a=ACTOR)==1
            result=post(cursor,command);checks.append("native_only_assigned_real_resource_canonical_execute")
            assert scalar(cursor,"select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'",o=operation)==1
            assert scalar(cursor,"select sum(REMAIN)from RRL_REMAINS where UID_POLETA=:u",u=LOT)==23
            assert scalar(cursor,"select sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:u",u=LOT)==0
            assert scalar(cursor,"select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:t",t=args.task)>0
            assert scalar(cursor,"select RRL_CASE_TASK_ACCESS.scoped_executor(:t,:a)from dual",t=args.task,a=ACTOR)==1
            cursor.callproc("RRL_CASE_TASK_ACCESS.assert_command",[command.canonical_json(),ACTOR]);checks.append("first_canonical_carrier_preserves_current_and_new_execution_scope")
            cursor.callproc("RRL_STOCK_POSTING_API.reset_connection")
            cursor.execute("select RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:o",{"o":operation})
            saved=read_oracle_json(cursor.fetchone()[0]);assert saved==result,(saved,result)
            checks.append("current_authorization_guard_and_exact_stored_applied_receipt")
            try:post(cursor,command)
            except oracledb.DatabaseError as error:assert error.args[0].code==20843,str(error)
            else:raise AssertionError("Strict dirty transaction replay unexpectedly accepted")
            checks.append("dirty_transaction_replay_refused_without_weakening_clean_plan")
            key="STOCK:"+hashlib.sha256(operation.encode()).hexdigest().upper()
            assert scalar(cursor,"select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:k",k=key)==1
        finally:
            connection.rollback();cursor.callproc("RRL_STOCK_POSTING_API.reset_connection")
    assert snapshot(gateway,args.task,line_id)==before
    for table,column,value in(("RRL_STOCK_OPERATION","OPERATION_ID",operation),("RRL_PALLETS","CREATED_BY_STOCK_OP",operation),("RRL_EVENT_OUTBOX","IDEMPOTENCY_KEY","STOCK:"+hashlib.sha256(operation.encode()).hexdigest().upper())):
        assert gateway.fetch_all("select count(*) N from "+table+" where "+column+"=:v",{"v":value})[0]["n"]==0,(table,value)
    checks.append("source_case_line_operation_newlots_outbox_exact_rollback")
    slow=gateway.fetch_all("select LOG_ID,ELAPSED_MS,API_PATH,dbms_lob.substr(SQL_TEXT,250,1) SQL_SAMPLE from RRL_SQL_SLOW_LOG where CREATED_AT>=systimestamp-interval'1'hour order by CREATED_AT desc fetch first 12 rows only")
    top_sql=gateway.fetch_all("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3) AVG_MS,substr(SQL_TEXT,1,300) SQL_SAMPLE
        from V$SQL where PARSING_SCHEMA_NAME=sys_context('USERENV','CURRENT_SCHEMA')and EXECUTIONS>0
        and LAST_ACTIVE_TIME>=sysdate-1/24 and SQL_TEXT not like '%V$SQL%'
        and((upper(SQL_TEXT)like '%RRL_CASE_PICK_LINE%'and upper(SQL_TEXT)like '%RRL_SKU_RECEIPT_PROFILE%')or upper(SQL_TEXT)like '%RRL_CASE_RESOURCE_POLICY.CONTEXT_JSON%')
        order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 10 rows only""")
    report={"status":"PASS","task_id":args.task,"line_id":line_id,"actor":ACTOR,"checks":checks,"result":result,"before_after":before,"stock_committed":False,"physical_verified":False,"recent_slow":slow,"oracle_relevant_top_sql":top_sql,"sql_scope":"Native-only suite; no HTTP/API-audit claim. V$SQL shared-cursor averages are diagnostic, not isolated load metrics.",
        "limits":["Second durable partial pick not proven: demand1 and strict cleanTX prohibit two new commands in one rollbackTX","Clean-transaction APPLIED replay requires a committed TEST receipt; deferred to separately approved ASM phase","Legacy SBORKA carrier-id populated CASE not produced by this current canonical pick; that regression remains separate"],
        "sql_decision":"PK CASE/task/line and CASE-bound SKU closure retained; no observed attributed >1000ms query requires index here; not capacity acceptance."}
    REPORT.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8");print(json.dumps({"status":"PASS","checks":checks,"task_id":args.task,"stock_committed":False}))


if __name__=="__main__":main()
