"""21 genuine native intents on isolated device; original CASE read-only, no fake captures; rollback."""
import json
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from warehouse_scale_requests_native import call,wire
from warehouse_scale_requests_fixture import REPORT,WARE,CELL,ACTOR,SENDER,stock
API="RRL_WH_WEIGH_REQUEST_API."


class RollbackTrial(Exception):
    pass


def run(expected_items:int)->None:
    gateway=OracleGateway();shared=json.loads(REPORT.read_text(encoding="utf-8-sig"));tag=uuid4().hex[:10]
    device="WH.PENDING.ROLLBACK:"+tag;prefix="WH.PENDING:"+tag
    before=stock(gateway)
    original=gateway.fetch_all("select *from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:task",{"task":shared["case"]})
    counter=0;task=None;label=None;result=None;current=None
    try:
        with gateway.transaction("Bounded21 native superseded intents; rollback only")as c:
            c.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
            try:
                task=shared["case"]
                c.execute("select SSCC,CONTENT_VERSION,RESOURCE_SESSION_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:task",task=task)
                carrier,version,session=c.fetchone()
                assert session is not None
                c.execute("""insert into RRL_WH_SCALE_DEVICE(DEVICE_ID,WARE_ID,POST_CELL,SENDER_ID,POLICY_VERSION,ACTIVE_FLAG,
                    DEVICE_MODE,MEASUREMENT_BASIS,CAPACITY_KG,RESOLUTION_KG,CALIBRATION_REF,CALIBRATED_UNTIL,CHANGED_BY)
                    values(:device,:ware,:cell,:sender,1,1,'TEST','GROSS',100,.001,'SIMULATED_ROLLBACK_NOT_HARDWARE',systimestamp+interval '1'day,'admin')""",
                    device=device,ware=WARE,cell=CELL,sender=SENDER)
                for index in range(1,22):
                    if index>1:c.execute("update RRL_WH_SCALE_DEVICE set POLICY_VERSION=POLICY_VERSION+1 where DEVICE_ID=:device",device=device)
                    body=dict(request_id=prefix+"."+str(index).zfill(2),device_id=device,purpose="EMPTY_TARE",
                        case_task_id=task,expected_content_version=int(version),scan_container=carrier,resource_session_id=int(session))
                    current=call(c,API+"request_capture",wire(body),ACTOR)
                    assert current["state"]=="REQUESTED",current
                    counter+=1
                newest=call(c,API+"request_status",current["request_id"],ACTOR)
                assert newest["state"]=="REQUESTED"
                result=call(c,API+"pending_requests",device,SENDER)
                assert len(result["items"])==expected_items,(expected_items,result)
                if expected_items:assert result["items"][0]["request_id"]==current["request_id"]
                c.execute("select count(*)from RRL_WH_SCALE_CAPTURE where DEVICE_ID=:device",device=device)
                assert c.fetchone()[0]==0,"No fabricated or real capture rows are needed for this regression"
            finally:c.callproc("RRL_STOCK_CONFIG_API.end_change")
            raise RollbackTrial()
    except RollbackTrial:
        pass
    assert counter==21
    for table,column,value in(("RRL_WH_WEIGH_REQUEST","DEVICE_ID",device),("RRL_WH_SCALE_DEVICE","DEVICE_ID",device)):
        assert gateway.fetch_all("select count(*)N from "+table+" where "+column+"=:value",{"value":value})[0]["n"]==0,(table,value)
    assert stock(gateway)==before
    assert gateway.fetch_all("select *from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:task",{"task":shared["case"]})==original
    output=dict(status="BEFORE_BUG_REPRODUCED"if expected_items==0 else"AFTER_PASS",native_created_intents=counter,
        fabricated_captures=0,newest_state="REQUESTED",pending_result=result,transaction_rollback_verified=True,
        original_case_unchanged=True,source_P_H_V_unchanged=True,physical_hardware=False,sequence_values_consumed_not_reused=False)
    filename="pending-before.json"if expected_items==0 else"pending-after.json"
    target=ROOT/"reports/retailcase/2026-10-15/warehouse-weigh-request"/filename
    target.write_text(json.dumps(output,indent=2),encoding="utf-8")
    print(json.dumps({key:output[key]for key in("status","native_created_intents","fabricated_captures","original_case_unchanged","transaction_rollback_verified")}))


if __name__=="__main__":
    run(int(sys.argv[1]))

