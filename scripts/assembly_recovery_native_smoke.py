"""Recovery on retained isolated CASE1032; all observations explicitly TEST, no goods posting."""
import argparse
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
from app.db import oracle_connection
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.assembly_scale import AssemblyScales,wire
from app.modules.inventory.contracts_assembly_recovery import AssemblyReconciliationRequest,AssemblyReconciliationAuthorization,AssemblyReconciliationCapture
from app.modules.inventory.contracts_assembly_scale import AssemblyStepOpen
from app.modules.platform.public import read_oracle_json
from assembly_scale_native_smoke import stamp,expect_refusal

SID,STEP,DEVICE,OPERATOR,SENDER="ASM15.S1032","ASM15.T1032","ASM15.CASE1032","ASM15.OP1032","ASM15.GW1032"
RID="ASM15.RECON1032"
REPORT=ROOT/"reports/retailcase/2026-10-15/assembly-scale/recovery-native.json"


def save(report):
    REPORT.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")


def forbidden_post(command):
    raise AssertionError("Recovery may not invoke a stock writer")


def native(q,method,*arguments):
    output=q.var(oracledb.DB_TYPE_CLOB)
    q.callproc("RRL_ASSEMBLY_RECOVERY_API."+method,[*arguments,output])
    return read_oracle_json(output.getvalue())


def snapshot(g):
    return dict(stock=g.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='FULL.QA:d9a5c53b54' order by CELL"),
        task=g.fetch_all("select CONTENT_VERSION,PICKED_QTY,STATUS,ASSIGNED_TO from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1032"),
        line=g.fetch_all("select PICKED_QTY,STATUS from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=1036"))


def stage(g,report):
    assert not REPORT.exists(),"Do not blindly recreate a retained intent"
    service=AssemblyScales(g,forbidden_post)
    before=snapshot(g)
    assert service.read_step(STEP,OPERATOR)["state"]=="DISCREPANCY"
    request=AssemblyReconciliationRequest(operation_id=RID,step_id=STEP,expected_content_version=2,reason="TEST_FIXTURE_NOT_HARDWARE hold before removing unaccepted goods")
    report.update(before=before,request=request.model_dump(),physical_verified=False,stock_posting_called=False)
    report["requested"]=service.request_reconciliation(SID,request,OPERATOR)
    assert report["requested"]["state"]=="REQUESTED"
    assert service.request_reconciliation(SID,request,OPERATOR)==report["requested"]
    session=service.read_session(SID,OPERATOR)
    assert session["state"]=="BLOCKED"and session["reconciliation"]["state"]=="REQUESTED"
    assert service.gateway_requests(DEVICE,SENDER)["items"]==[]
    save(report)
    authorization=AssemblyReconciliationAuthorization(operation_id="ASM15.RECON.AUTH1032",reason="TEST_FIXTURE_NOT_HARDWARE distinct controller after HOLD",unaccepted_goods_removed=True)
    with oracle_connection()as con:
        q=con.cursor()
        try:
            output=q.var(oracledb.DB_TYPE_CLOB)
            report["self_approval"]=expect_refusal(q,"RRL_ASSEMBLY_RECOVERY_API.authorize",[RID,wire(authorization),OPERATOR,output],"ASSEMBLY_RECOVERY_DISTINCT_CONTROLLER_REQUIRED")
        finally:con.rollback()
    report["authorized"]=service.authorize_reconciliation(RID,authorization,"admin")
    assert report["authorized"]["state"]=="AUTHORIZED"and report["authorized"]["controller_id"]!=OPERATOR
    assert service.authorize_reconciliation(RID,authorization,"admin")==report["authorized"]
    report["authorization"]=authorization.model_dump()
    report["queue"]=service.gateway_requests(DEVICE,SENDER)["items"][0]
    assert report["queue"]["phase"]=="RECONCILE"and report["queue"]["reconciliation_id"]==RID
    assert snapshot(g)==before
    report["status"]="AUTHORIZED_FOR_NATIVE_ROLLBACK_THEN_REAL_OPC_HTTP"
    save(report)


def rollback_capture(g,report):
    service=AssemblyScales(g,forbidden_post)
    request=service.gateway_requests(DEVICE,SENDER)["items"][0]
    time.sleep(2.1)
    packet=AssemblyReconciliationCapture(session_id=SID,step_id=STEP,capture_id=request["capture_id"],phase="RECONCILE",reconciliation_id=RID,
        device_id=DEVICE,device_policy_version=request["device_policy_version"],calibration_ref=request["calibration_ref"],unit="KG",basis="GROSS",preset_tare_kg="0",
        tare_mode_clear=True,quality_confirmed=True,measured_at=stamp(),samples=[{"offset_ms":i*500,"weight_kg":"0.5"}for i in range(5)])
    before=snapshot(g)
    with oracle_connection()as con:
        q=con.cursor()
        try:
            acknowledgement=native(q,"capture",wire(packet),SENDER)
            assert acknowledgement["state"]=="COMPLETED"and acknowledgement["stock_posted"]is False
            assert native(q,"capture",wire(packet),SENDER)==acknowledgement
            q.execute("select STATE from RRL_ASSEMBLY_STEP where STEP_ID=:s",s=STEP)
            assert q.fetchone()==("CANCELLED",)
            q.execute("select STATE,LAST_WEIGHT_KG,LAST_CONTENT_VERSION from RRL_ASSEMBLY_SESSION where SESSION_ID=:s",s=SID)
            assert q.fetchone()==("OPEN",0.5,2)
            report["native_matching_rollback"]={"archive":acknowledgement,"step":"CANCELLED","session":"OPEN","last_weight":"0.5","content_version":2}
            guarded=[]
            for sql,marker in (("update RRL_ASM_RECON_CAPTURE set SOURCE_SHA256='0'where RECONCILIATION_ID=:r","ASSEMBLY_RECONCILIATION_CAPTURE_APPEND_ONLY"),
                               ("delete from RRL_ASM_RECON_CAPTURE where RECONCILIATION_ID=:r","ASSEMBLY_RECONCILIATION_CAPTURE_APPEND_ONLY")):
                try:q.execute(sql,r=RID)
                except oracledb.DatabaseError as error:assert marker in str(error),(marker,str(error))
                else:raise AssertionError(marker)
                guarded.append(marker)
            try:q.callproc("RRL_ASSEMBLY_SCALE_API.apply_reconciliation",[RID,SID,STEP])
            except oracledb.DatabaseError as error:assert "ASSEMBLY_RECOVERY_TRUSTED_APPLY_REQUIRED"in str(error)
            else:raise AssertionError("Direct privileged hook accepted")
            report["native_matching_rollback"]["append_only_and_trusted_hook_guards"]=guarded+["ASSEMBLY_RECOVERY_TRUSTED_APPLY_REQUIRED"]

        finally:con.rollback()
    assert snapshot(g)==before
    assert service.read_step(STEP,OPERATOR)["state"]=="DISCREPANCY"
    assert service.read_reconciliation(RID,OPERATOR)["state"]=="AUTHORIZED"
    assert not g.fetch_all("select CAPTURE_ID from RRL_ASM_RECON_CAPTURE where RECONCILIATION_ID=:r",{"r":RID})
    assert g.fetch_all("select count(*)N from RRL_STOCK_OPERATION where OPERATION_ID='ASM15.PICK1032'")[0]["n"]==0
    report["native_matching_rollback"]["all_metadata_effects_rolled_back_no_goods_or_operation"]=True
    report["status"]="AUTHORIZED_RETAINED_FOR_REAL_OPC_HTTP"
    save(report)



def negative_guards(g,report):
    service=AssemblyScales(g,forbidden_post)
    queue=service.gateway_requests(DEVICE,SENDER)["items"][0]
    before=snapshot(g)
    checks=[]
    changed={**report["request"],"reason":"Changed request identity TEST"}
    new={**report["request"],"operation_id":"ASM15.RECON.CONFLICT1032"}
    with oracle_connection()as con:
        q=con.cursor()
        try:
            output=q.var(oracledb.DB_TYPE_CLOB)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_RECOVERY_API.request_reconciliation",[SID,json.dumps(changed),OPERATOR,output],"ASSEMBLY_RECOVERY_REQUEST_CONFLICT"))
        finally:con.rollback()
    with oracle_connection()as con:
        q=con.cursor()
        try:
            output=q.var(oracledb.DB_TYPE_CLOB)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_RECOVERY_API.request_reconciliation",[SID,json.dumps(new),OPERATOR,output],"ASSEMBLY_RECOVERY_ACTIVE_INTENT_CONFLICT"))
        finally:con.rollback()
    packet=AssemblyReconciliationCapture(session_id=SID,step_id=STEP,capture_id=queue["capture_id"],phase="RECONCILE",reconciliation_id=RID,
        device_id=DEVICE,device_policy_version=queue["device_policy_version"],calibration_ref=queue["calibration_ref"],unit="KG",basis="GROSS",preset_tare_kg="0",
        tare_mode_clear=True,quality_confirmed=True,measured_at=stamp(),samples=[{"offset_ms":i*500,"weight_kg":"3.5"}for i in range(5)])
    with oracle_connection()as con:
        q=con.cursor()
        try:
            ack=native(q,"capture",wire(packet),SENDER)
            assert ack["state"]=="DISCREPANCY"
            q.execute("select STATE from RRL_ASSEMBLY_SESSION where SESSION_ID=:s",s=SID)
            assert q.fetchone()==("BLOCKED",)
            report["mismatch_rollback"]={"archive_state":"DISCREPANCY","session":"BLOCKED","step_uncancelled":True}
        finally:con.rollback()
    with oracle_connection()as con:
        q=con.cursor()
        try:
            output=q.var(oracledb.DB_TYPE_CLOB)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_RECOVERY_API.capture",[wire(packet),OPERATOR,output],"ASSEMBLY_RECOVERY_DEDICATED_SENDER_REQUIRED"))
            q.execute("update RUSERS set DELETED=1 where ID=:a",a=OPERATOR)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_RECOVERY_API.capture",[wire(packet),SENDER,output],"ASSEMBLY_RECOVERY_CURRENT_PERMISSION_REQUIRED"))
        finally:con.rollback()
    with oracle_connection()as con:
        q=con.cursor()
        try:
            for sql in ("update RRL_ASM_RECONCILIATION set STATE='COMPLETED'where RECONCILIATION_ID=:r","delete from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=:r","insert into RRL_ASM_RECONCILIATION select *from RRL_ASM_RECONCILIATION where RECONCILIATION_ID=:r"):
                try:q.execute(sql,r=RID)
                except oracledb.DatabaseError as error:assert "ASSEMBLY_RECONCILIATION_OWNER_REQUIRED"in str(error),str(error)
                else:raise AssertionError("Direct recovery metadata mutation accepted")
                checks.append("ASSEMBLY_RECONCILIATION_OWNER_REQUIRED")
        finally:con.rollback()
    assert snapshot(g)==before
    assert service.read_reconciliation(RID,OPERATOR)["state"]=="AUTHORIZED"
    assert service.read_step(STEP,OPERATOR)["state"]=="DISCREPANCY"
    report["negative_guards"]=checks
    report["status"]="NATIVE_GUARDS_PASS_AUTHORIZED_FOR_REAL_OPC_HTTP"
    save(report)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--stage-approved-intent",action="store_true")
    parser.add_argument("--matching-capture-rollback",action="store_true")
    parser.add_argument("--negative-guards",action="store_true")
    args=parser.parse_args()
    g=OracleGateway()
    if args.stage_approved_intent:stage(g,{})
    elif args.negative_guards:negative_guards(g,json.loads(REPORT.read_text(encoding="utf-8")))
    elif args.matching_capture_rollback:rollback_capture(g,json.loads(REPORT.read_text(encoding="utf-8")))
    else:raise SystemExit("Explicit isolated test action required")
    print(json.dumps({"report":str(REPORT),"goods_commit":False,"physical_verified":False}))


if __name__=="__main__":main()
