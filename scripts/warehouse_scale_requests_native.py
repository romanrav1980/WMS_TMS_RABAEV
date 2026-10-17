"""Shared QA warehouse request proof. Archive-only caller rollback plus approved EMPTY stage."""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.modules.inventory.infrastructure.warehouse_scale_requests import WarehouseWeighRequests
from app.modules.inventory.infrastructure.warehouse_scales import WarehouseScales
from app.modules.inventory.contracts_warehouse_scale import WarehouseScaleConfiguration,WarehouseFinalScalePacket
from app.modules.inventory.infrastructure.tare_assembly import TareAssembly
from app.modules.integrations.public import validate_warehouse_ack
from app.modules.integrations.contracts_warehouse_gateway import WarehouseGatewayProfile
from warehouse_scale_requests_fixture import command,stock,save,REPORT,WARE,CELL,ACTOR,SENDER,PREFIX,NOTE
API="RRL_WH_WEIGH_REQUEST_API."
DEVICE="WHREQ15.SCALE"
CALIBRATION="SIMULATED_TEST_NOT_HARDWARE:WHREQ15"
OUT=ROOT/"reports/retailcase/2026-10-15/warehouse-weigh-request/native.json"


def wire(body:dict[str,Any])->str:
    return json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def call(cursor:Any,method:str,*arguments:Any)->dict[str,Any]:
    result=cursor.var(oracledb.DB_TYPE_CLOB)
    cursor.callproc(method,[*arguments,result])
    return read_oracle_json(result.getvalue())


def reject(cursor:Any,method:str,arguments:list[Any],reason:str)->None:
    try:call(cursor,method,*arguments)
    except oracledb.DatabaseError as error:assert reason in str(error),(reason,str(error))
    else:raise AssertionError("Expected refusal "+reason)


def stamp(value:datetime)->str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")


def packet(context:dict[str,Any],now:datetime|None=None)->dict[str,Any]:
    now=now or datetime.now(timezone.utc)
    return {**context,"zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=10)),
        "measured_at":stamp(now),"samples":[dict(offset_ms=i*500,weight_kg="0.5")for i in range(5)]}


def prepare(gateway:OracleGateway,ctx:dict[str,Any])->dict[str,Any]:
    if not all(key in ctx for key in ("tare_count","tare_book","device")):
        tare=TareAssembly(gateway)
        available=next(row for row in tare.availability(WARE,"admin")if row["pallet_type_id"]==32)
        ctx["tare_before"]=available;save(ctx)
        assert available["assembly_quantity"] in(None,"0"),available
        old=int(available["physical_quantity"]or 0)
        assert old==0,"Shared QA must not consume existing physical tare"
        ctx["tare_count"]=command("TARE_COUNT",PREFIX+".TARE.COUNT",{},dict(owner_ware_id=WARE,pallet_type_id=32,condition="GOOD",
            observed_quantity="1",expected_version=int(available["balance_version"]or 0),reason=NOTE,decision_reference=PREFIX))
        ctx["tare_book"]=command("TARE_BOOK",PREFIX+".TARE.BOOK",dict(place_kind="CASE",place_id=str(ctx["case"])),dict(pallet_type_id=32,expected_warehouse_id=WARE))
        config=WarehouseScaleConfiguration(warehouse_id=WARE,post_cell=CELL,sender_id=SENDER,expected_version=0,active=True,device_mode="TEST",
            basis="GROSS",capacity_kg="100",resolution_kg="0.001",calibration_ref=CALIBRATION,calibrated_until=stamp(datetime.now(timezone.utc)+timedelta(days=1)))
        ctx["device"]=WarehouseScales(gateway).configure(DEVICE,config,"admin");save(ctx)
    else:
        held=gateway.fetch_all("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:op",{"op":PREFIX+".TARE.BOOK"})
        assert held==[{"status":"HELD"}],held
    current=gateway.fetch_all("select CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:task",{"task":ctx["case"]})[0]
    resource=json.loads((ROOT/"reports/retailcase/2026-10-15/scoped-case-audit/shared-resources.json").read_text(encoding="utf-8-sig"))
    assert resource["task_id"]==ctx["case"]and resource["actor"]==ACTOR
    return dict(request_id=PREFIX+".EMPTY",device_id=DEVICE,purpose="EMPTY_TARE",case_task_id=ctx["case"],
        expected_content_version=int(current["content_version"]),scan_container=current["sscc"],resource_session_id=resource["session_id"])


def rollback_cases(gateway:OracleGateway,body:dict[str,Any])->list[str]:
    checks=[];temp={**body,"request_id":PREFIX+".ROLLBACK"}
    before=stock(gateway)
    try:
        with gateway.transaction("Archive-only weighing queue caller rollback")as c:
            c.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
            try:
                first=call(c,API+"request_capture",wire(temp),ACTOR)
                assert first["state"]=="REQUESTED"and first["capture_key"]is None
                assert call(c,API+"request_capture",wire(temp),ACTOR)==first
                reject(c,API+"request_capture",[wire({**temp,"scan_container":"WRONG"}),ACTOR],"PAYLOAD_CONFLICT")
                reject(c,API+"request_capture",[wire(temp),SENDER],"ORIGINAL_ACTOR_REQUIRED")
                reject(c,API+"request_capture",[wire({**temp,"request_id":PREFIX+".BUSY"}),ACTOR],"DEVICE_BUSY")
                checks+=["exact_intent","immutable_body_conflict","original_actor","device_busy"]
                pending=call(c,API+"pending_requests",DEVICE,SENDER)
                assert [row["request_id"]for row in pending["items"]]==[temp["request_id"]]
                reject(c,API+"pending_requests",[DEVICE,ACTOR],"DEDICATED_SENDER")
                checks.append("dedicated_sender_poll_only")
                claim=dict(claim_id=PREFIX+".ROLLBACK.C1",device_id=DEVICE)
                owned=call(c,API+"claim_request",temp["request_id"],wire(claim),SENDER)
                assert owned["claim_active"]is True and "samples"not in owned["capture_context"]
                assert call(c,API+"claim_request",temp["request_id"],wire(claim),SENDER)==owned
                reject(c,API+"claim_request",[temp["request_id"],wire({**claim,"claim_id":PREFIX+".ROLLBACK.C2"}),SENDER],"NOT_CLAIMABLE")
                checks+=["fixed_exact_claim_lease","second_claim_busy"]
                source=packet(owned["capture_context"])
                reject(c,"RRL_WH_SCALE_API.capture",[wire({**source,"capture_id":"ORPHAN"}),SENDER],"ACTIVE_REQUEST_CLAIM_REQUIRED")
                reject(c,"RRL_WH_SCALE_API.capture",[wire({**source,"scan_container":"WRONG"}),SENDER],"INTENT_MISMATCH")
                reject(c,"RRL_WH_SCALE_API.capture",[wire(source),SENDER],"OBSERVATION_OUTSIDE_CLAIM")
                checks+=["orphan_packet_denied","capture_context_fenced","cached_preclaim_series_denied"]
                time.sleep(2.15)
                source=packet(owned["capture_context"])
                archived=call(c,"RRL_WH_SCALE_API.capture",wire(source),SENDER)
                profile=WarehouseGatewayProfile(device_id=DEVICE,warehouse_id=WARE,post_cell=CELL,device_mode="TEST",device_policy_version=1,calibration_ref=CALIBRATION,basis="GROSS")
                validate_warehouse_ack(wire(source).encode(),wire(archived).encode(),profile)
                status=call(c,API+"request_status",temp["request_id"],ACTOR)
                assert status["state"]=="CAPTURED"and status["capture_key"]==archived["capture_key"]and not status["stock_posted"]
                assert call(c,"RRL_WH_SCALE_API.capture",wire(source),SENDER)==archived
                checks+=["strict_real_native_ack","derived_capture_key_not_stock_posted","exact_archive_ack"]
                reject(c,"RRL_WH_SCALE_API.capture",[wire({**source,"zero_check_kg":"0.01"}),SENDER],"PAYLOAD_CONFLICT")
                c.execute("savepoint sender_transfer")
                c.execute("insert into RIGHTS(RIGHT1,USER_GROUP,DESCR)values('warehouse_scale_ingest','WHREQ15.OP','Temporary callerrollback transfer test')")
                c.execute("update RRL_WH_SCALE_DEVICE set SENDER_ID=:actor,POLICY_VERSION=POLICY_VERSION+1 where DEVICE_ID=:device",actor=ACTOR,device=DEVICE)
                reject(c,"RRL_WH_SCALE_API.capture",[wire(source),ACTOR],"ORIGINAL_ARCHIVE_SENDER_REQUIRED")
                c.execute("rollback to sender_transfer");checks.append("reassigned_sender_cannot_inherit_original_ack")
                c.execute("update RUSERS set DELETED=1 where ID=:actor",actor=ACTOR)
                reject(c,API+"request_status",[temp["request_id"],ACTOR],"ACTIVE_USER_REQUIRED")
                reject(c,API+"request_capture",[wire(temp),ACTOR],"ACTIVE_USER_REQUIRED")
                c.execute("update RUSERS set DELETED=0 where ID=:actor",actor=ACTOR)
                checks.append("revoked_operator_cannot_read_or_replay_request")
                for table,key in(("RRL_WH_WEIGH_REQUEST","REQUEST_ID"),("RRL_WH_WEIGH_CLAIM","CLAIM_ID")):
                    try:c.execute("delete from "+table+" where "+key+"=:key",key=temp["request_id"]if key=="REQUEST_ID"else claim["claim_id"])
                    except oracledb.DatabaseError as error:assert "APPEND_ONLY"in str(error),str(error)
                    else:raise AssertionError("Immutable history deleted")
                checks.append("request_and_claim_append_only")
            finally:c.callproc("RRL_STOCK_CONFIG_API.end_change")
            raise RollbackTrial()
    except RollbackTrial:pass
    assert gateway.fetch_all("select count(*)N from RRL_WH_WEIGH_REQUEST where REQUEST_ID=:id",{"id":temp["request_id"]})[0]["n"]==0
    assert gateway.fetch_all("select count(*)N from RRL_WH_SCALE_CAPTURE where CAPTURE_ID=:id",{"id":PREFIX+".ROLLBACK.C1"})[0]["n"]==0
    assert stock(gateway)==before
    assert gateway.fetch_all("select SENDER_ID,POLICY_VERSION from RRL_WH_SCALE_DEVICE where DEVICE_ID=:id",{"id":DEVICE})==[{"sender_id":SENDER,"policy_version":1}]
    assert gateway.fetch_all("select DELETED from RUSERS where ID=:id",{"id":ACTOR})==[{"deleted":0}]
    checks.append("all_archive_request_claim_and_fixture_changes_rollback_P_H_V_unchanged")
    return checks


class RollbackTrial(Exception):
    pass


def durable_empty(gateway:OracleGateway,ctx:dict[str,Any],body:dict[str,Any],checks:list[str])->None:
    service=WarehouseWeighRequests(gateway)
    ctx["empty_request_body"]=body;ctx["empty_request"]=service.request(body,ACTOR);save(ctx)
    def compete(claim_id:str)->dict[str,Any]:
        claim=dict(claim_id=claim_id,device_id=DEVICE)
        try:return dict(ok=True,body=claim,result=service.claim(body["request_id"],claim,SENDER))
        except Exception as error:return dict(ok=False,error=str(error),status=getattr(error,"status",None))
    with ThreadPoolExecutor(max_workers=2)as pool:
        results=list(pool.map(compete,[PREFIX+".EMPTY.C1A",PREFIX+".EMPTY.C1B"]))
    assert sum(row["ok"]for row in results)==1,results
    assert next(row for row in results if not row["ok"])["status"]==409,results
    winner=next(row for row in results if row["ok"]);ctx["claim_competition"]=results;save(ctx)
    checks.append("two_simultaneous_claims_one_winner_one_definite_busy")
    time.sleep(31)
    late=packet(winner["result"]["capture_context"])
    with gateway.transaction("Reject late first archive after real lease expiration")as c:
        reject(c,"RRL_WH_SCALE_API.capture",[wire(late),SENDER],"LATE_FIRST_CAPTURE_REJECTED")
    replay=service.claim(body["request_id"],winner["body"],SENDER)
    assert replay["claim_active"]is False and replay["capture_key"]is None
    checks.append("expired_claim_cannot_archive_or_renew_exact_retry")
    fresh=service.claim(body["request_id"],dict(claim_id=PREFIX+".EMPTY.C2",device_id=DEVICE),SENDER)
    time.sleep(2.15)
    source=packet(fresh["capture_context"]);ctx["empty_capture_body"]=source;save(ctx)
    archived=WarehouseScales(gateway).capture(WarehouseFinalScalePacket(**source),SENDER)
    ctx["empty_archive"]=archived;ctx["empty_status"]=service.status(body["request_id"],ACTOR)
    assert ctx["empty_status"]["state"]=="CAPTURED"and ctx["empty_status"]["current_context"]=="CURRENT"
    assert not ctx["empty_status"]["stock_posted"]
    ctx["state"]="EMPTY_CAPTURED_AWAIT_CLAIM_START";save(ctx)
    checks.append("new_fenced_claim_after_proven_absence_archives_one_EMPTY_without_stock")
    OUT.write_text(json.dumps(dict(status="PASS",checks=checks,stock=stock(gateway),stock_effect="NONE_FROM_QUEUE",physical_hardware=False),indent=2,default=str),encoding="utf-8")
    print(json.dumps(dict(status="PASS",checks=len(checks),state=ctx["state"],capture_key=archived["capture_key"])))


def main()->None:
    assert os.environ.get("RUN_APPROVED_WH_METADATA_STAGE")=="1"
    gateway=OracleGateway();ctx=json.loads(REPORT.read_text(encoding="utf-8-sig"))
    assert "empty_archive" not in ctx,"Completed shared stage exists; never rerun/fork its physical observation"
    body=prepare(gateway,ctx)
    checks=rollback_cases(gateway,body)
    durable_empty(gateway,ctx,body,checks)


if __name__=="__main__":
    main()

