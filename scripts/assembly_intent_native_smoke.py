"""Only isolated CASE1136 metadata; never invokes a goods writer.
Run after scoped fixture owner restores temporary flat execution access.
"""
import json,sys,time,threading
from pathlib import Path
import oracledb,httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
ACTOR="WHREQ15.OP";TASK=1136;SID="WHREQ15.ABSENT.SESSION";RID="WHREQ15.ABSENT.ABANDON"
OUT=ROOT/"reports/retailcase/2026-10-15/assembly-intent/native.json"

def wire(v):return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)
def call(q,method,*args):
    o=q.var(oracledb.DB_TYPE_CLOB);q.callproc(method,[*args,o]);return read_oracle_json(o.getvalue())
def deny(q,method,args,marker):
    try:call(q,method,*args)
    except oracledb.DatabaseError as e:assert marker in str(e),(marker,str(e));return marker
    raise AssertionError("Unexpected acceptance "+marker)
def snapshot(g):
    return dict(stock=g.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd' order by CELL"),task=g.fetch_all("select STATUS,PICKED_QTY,CONTENT_VERSION,ASSIGNED_TO from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136"))
def main():
    g=OracleGateway();before=snapshot(g);assert before["task"][0]["assigned_to"]==ACTOR
    assert g.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute') N from dual",{"a":ACTOR})[0]["n"]==1,"WAIT_FLAT_OWNER_RELEASE"
    task=g.fetch_all("select CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":TASK})[0]
    original=dict(session_id=SID,task_id=TASK,device_id="WHREQ15.NO_DEVICE",expected_content_version=task["content_version"],tare_capture_key="0"*64,scan_container=task["sscc"])
    body=dict(operation_id=RID,kind="OPEN_SESSION",reason="TEST_NOT_HARDWARE explicit never-created attempt abandonment",original=original)
    checks=[];base=g.fetch_all("select count(*) N from RRL_ASM_INTENT_ABANDON")[0]["n"]
    with oracle_connection()as c:
        q=c.cursor()
        try:
            ack=call(q,"RRL_ASM_INTENT_API.abandon",wire(body),ACTOR)
            assert ack["status"]=="ABANDONED"and ack["original"]==original and ack["stock_posted"]is False
            assert call(q,"RRL_ASM_INTENT_API.describe",RID,ACTOR)==ack
            checks.append("native_absent_receipt_and_read_inside_caller_owned_TX")
            checks.append(deny(q,"RRL_ASM_INTENT_API.describe",[RID,"admin"],"ASSEMBLY_INTENT_CURRENT_OPERATOR_REQUIRED"))
            checks.append(deny(q,"RRL_ASM_INTENT_API.abandon",[wire(body),None],"ASSEMBLY_INTENT_CURRENT_OPERATOR_REQUIRED"))
            for sql in("delete from RRL_ASM_INTENT_ABANDON where ABANDONMENT_ID=:r","update RRL_ASM_INTENT_ABANDON set SOURCE_SHA256='0'where ABANDONMENT_ID=:r"):
                try:q.execute(sql,r=RID)
                except oracledb.DatabaseError as e:assert "ASSEMBLY_INTENT_LEDGER_APPEND_ONLY"in str(e)
                else:raise AssertionError("direct mutation accepted")
            checks.append("append_only_update_delete_denied")
            foreign=dict(operation_id="WHREQ15.FOREIGN.ABANDON",kind="OPEN_STEP",session_id="ASM15.S1031",reason="TEST foreign parent must fail",original=dict(step_id="WHREQ15.FOREIGN.STEP",operation_id="WHREQ15.FOREIGN.OP",case_line_id=1139,quantity="1",scan_source_cell="QIPcdbf4c0962",scan_product="REUSE.QA:cdbf4c0962",scan_container=task["sscc"],expected_content_version=task["content_version"],consent_to_auto=True))
            checks.append(deny(q,"RRL_ASM_INTENT_API.abandon",[wire(foreign),ACTOR],"ASSEMBLY_INTENT_ORIGINAL_SESSION_OPERATOR_REQUIRED"))
        finally:c.rollback()
    assert snapshot(g)==before and g.fetch_all("select count(*) N from RRL_ASM_INTENT_ABANDON")[0]["n"]==base
    checks.append("caller_rollback_restores_entire_absent_ledger_and_source")
    # Explicit metadata-only durable receipt for production HTTP/late retry proof.
    late_result={};started=threading.Event();done=threading.Event()
    def late_open():
        with oracle_connection()as other:
            q=other.cursor();q.callproc("dbms_application_info.set_module",["ASM_INTENT_OLD_OPEN","WHREQ15"])
            started.set()
            try:late_result["denial"]=deny(q,"RRL_ASSEMBLY_SCALE_API.open_session",[wire(original),ACTOR],"ASSEMBLY_INTENT_ABANDONED_DO_NOT_RETRY")
            except Exception as error:late_result["error"]=str(error)
            finally:other.rollback();done.set()
    with oracle_connection()as c:
        q=c.cursor();ack=call(q,"RRL_ASM_INTENT_API.abandon",wire(body),ACTOR)
        # If recovering a previously committed exact receipt, do not re-claim first-create concurrency.
        if base==0:
            worker=threading.Thread(target=late_open,daemon=True);worker.start();assert started.wait(2)
            q.execute("select to_number(sys_context('USERENV','SID'))from dual");sid=q.fetchone()[0];waiting=[]
            for _ in range(20):
                q.execute("select EVENT,BLOCKING_SESSION from V$SESSION where MODULE='ASM_INTENT_OLD_OPEN'and ACTION='WHREQ15'and BLOCKING_SESSION=:s",s=sid);waiting=q.fetchall()
                if waiting:break
                time.sleep(.05)
            assert waiting and not done.is_set(),("Actual Oracle open wait not observed",late_result)
            c.commit();assert done.wait(10)and "error"not in late_result,late_result
            checks.append("actual_Oracle_wait_open_after_abandon_then_committed_tombstone_denies_late_create")
        else:c.commit()
    with oracle_connection()as c:
        q=c.cursor()
        try:
            assert call(q,"RRL_ASM_INTENT_API.abandon",wire(body),ACTOR)==ack
            checks.append("native_exact_receipt_replay_in_clean_transaction")
        finally:c.rollback()
    with oracle_connection()as c:
        try:checks.append(deny(c.cursor(),"RRL_ASM_INTENT_API.abandon",[wire({**body,"reason":"Different explicit reason"}),ACTOR],"ASSEMBLY_INTENT_ABANDONMENT_CONFLICT"))
        finally:c.rollback()
    secret=json.loads((ROOT/"runtime/warehouse-weigh-qa-secrets.json").read_text())
    url="http://127.0.0.1:8088/api/inventory/assembly-scale"
    with httpx.Client(auth=(ACTOR,secret[ACTOR]),timeout=15)as h:
        for response in(h.get(url+"/abandonments/"+RID),h.post(url+"/abandonments",json=body)):
            assert response.status_code==200 and response.json()==ack,(response.status_code,response.text)
        checks.append("production_HTTP_exact_original_owner_receipt_replay")
        late=h.post(url+"/sessions",json=original);assert late.status_code==409 and "ASSEMBLY_INTENT_ABANDONED_DO_NOT_RETRY"in late.text,late.text
        checks.append("production_HTTP_late_original_open_permanently_fenced")
    assert snapshot(g)==before
    assert not g.fetch_all("select SESSION_ID from RRL_ASSEMBLY_SESSION where SESSION_ID=:s",{"s":SID})
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(dict(status="PASS",checks=checks,body=body,ack=ack,before=before,after=snapshot(g),stock_posted=False,note="Append-only metadata receipt retained; no physical hardware evidence"),indent=2,default=str),encoding="utf-8")
    print(json.dumps(dict(status="PASS",checks=len(checks),stock_posted=False)))
if __name__=="__main__":main()
