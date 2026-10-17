"""Reviewed isolated role v1->2 inactive->3 active; quantity execution caller rollback."""
import json
import sys
import threading
from contextlib import contextmanager
import time
from pathlib import Path
from datetime import datetime
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from case_scoped_confirmation_native_smoke import ACTOR,REPORT,scalar,post,snapshot


def role(active,version,operation,gateway=None):
    payload=dict(role_id="WHREQ15.CASE.EXEC",title="TEST_FIXTURE_NOT_HARDWARE shared scoped CASE proof; metadata only",permissions=["case_pick_execute"],active=active,expected_version=version)
    return AccessMetadataService(gateway or OracleGateway()).command("admin",normalize(Command(operation_id=operation,command_type="ROLE_SAVE",payload=payload),"ACCESS"))


def main():
    proof=json.loads(REPORT.read_text(encoding="utf-8"));assert proof["status"]=="PASS"
    task,line=proof["task_id"],proof["line_id"];gateway=OracleGateway()
    rows=gateway.fetch_all("select l.CELL_CODE,l.ARTICUL,t.SSCC from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where l.CASE_PICK_LINE_ID=:l and t.CASE_PICK_TASK_ID=:t",{"l":line,"t":task});assert len(rows)==1
    r=rows[0];operation="WHREQ15.SCOPED.REVOKE.ROLLBACK"
    command=StockCommand(operation,"CASE_PICK_CONFIRM",ACTOR,(),{"case_task_id":task,"case_line_id":line},metadata={"fact_qty":"1","scan_cell":r["cell_code"],"scan_product":r["articul"],"scan_container":r["sscc"],"offline_event_id":None})
    before=snapshot(gateway,task,line);started=threading.Event();done=threading.Event();result={}
    class ObservedGateway(OracleGateway):
        @contextmanager
        def transaction(self,label):
            with super().transaction(label)as cursor:
                cursor.callproc("dbms_application_info.set_module",["CASE_SCOPED_REVOKE","WHREQ15"])
                started.set()
                try:yield cursor
                finally:cursor.callproc("dbms_application_info.set_module",[None,None])
    def revoke():
        try:result["deactivation"]=role(False,1,"WHREQ15.CASE.ROLE.REVOKE",ObservedGateway())
        except Exception as error:result["error"]=str(error)
        finally:done.set()
    worker=None
    try:
        with oracle_connection()as connection:
            cursor=connection.cursor()
            try:
                executed=post(cursor,command)
                worker=threading.Thread(target=revoke,daemon=True);worker.start();assert started.wait(2)
                sid=scalar(cursor,"select to_number(sys_context('USERENV','SID'))from dual")
                blocking=[]
                for attempt in range(15):
                    cursor.execute("select EVENT,WAIT_CLASS,SID,BLOCKING_SESSION from V$SESSION where MODULE='CASE_SCOPED_REVOKE'and ACTION='WHREQ15'and BLOCKING_SESSION=:sid",{"sid":sid})
                    blocking=cursor.fetchall()
                    if blocking:break
                    time.sleep(.05)
                assert blocking,("No actual Oracle wait on stock session observed",result)
                result["oracle_blocking_wait"]=[dict(event=row[0],wait_class=row[1],waiter_sid=row[2],blocking_sid=row[3])for row in blocking]
                assert not done.is_set(),("Revocation crossed uncommitted stock authorization fence",result)
            finally:connection.rollback();cursor.callproc("RRL_STOCK_POSTING_API.reset_connection")
        assert done.wait(10),"Revocation failed to finish after stock rollback"
        assert "error"not in result,result
        assert snapshot(gateway,task,line)==before
        assert gateway.fetch_all("select RRL_CASE_TASK_ACCESS.has_current_scoped_execute(:t,:a) N from dual",{"t":task,"a":ACTOR})==[{"n":0}]
        with oracle_connection()as connection:
            cursor=connection.cursor()
            try:
                try:post(cursor,command)
                except oracledb.DatabaseError as error:assert error.args[0].code==20882,str(error)
                else:raise AssertionError("Revoked executor admitted")
            finally:connection.rollback();cursor.callproc("RRL_STOCK_POSTING_API.reset_connection")
        result["current_revoke_denied"]=True
    finally:
        if worker:worker.join(12)
        state=gateway.fetch_all("select ACTIVE,VERSION_NO from RRL_ACCESS_ROLE where ROLE_ID='WHREQ15.CASE.EXEC'")
        if state==[{"active":0,"version_no":2}]:result["reactivation"]=role(True,2,"WHREQ15.CASE.ROLE.RESTORE")
        else:assert state==[{"active":1,"version_no":1}],("Unexpected owned role state; inspect native operation receipt",state,result)
    assert gateway.fetch_all("select RRL_CASE_TASK_ACCESS.has_current_scoped_execute(:t,:a) N from dual",{"t":task,"a":ACTOR})==[{"n":1}]
    assert snapshot(gateway,task,line)==before
    assert not gateway.fetch_all("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:o",{"o":operation})
    result.update(status="PASS",task_id=task,stock_committed=False,physical_verified=False,role_versions=[1,2,3],stock_before_after=before,
        evidence="Revocation blocked during canonical uncommitted stock execution; stock rollback releases fence, revoke then denies current guard and original operation; role restored by native owner",
        limitation="No committed APPLIED receipt existed for this rollback operation; durable old receipt after downstream progress is separate")
    output=REPORT.parent/"revoke-concurrency.json";output.write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"status":"PASS","task_id":task,"role_versions":[1,2,3],"stock_committed":False}))


if __name__=="__main__":main()
