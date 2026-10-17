"""Isolated DEV QA contracts only: simulated label/mass; quantitative effects always rollback.
Root explicitly approved CASE1031/wave395/type32/TEST prefix900000 and dedicated actors.
Metadata histories remain. No physical printer, scanner, scales or QC acceptance is claimed.
"""
import argparse
import json
import secrets
import sys
import time
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
import oracledb
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.platform.public import read_oracle_json, stock_configuration_transaction
from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
from app.modules.inventory.infrastructure.case_labels import CaseLabels
from app.modules.inventory.contracts_case_labels import CaseSsccLabelRequest
from app.modules.inventory.infrastructure.warehouse_scales import WarehouseScales
from app.modules.inventory.contracts_warehouse_scale import WarehouseScaleConfiguration, WarehouseFinalScalePacket
from app.modules.inventory.infrastructure.assembly_scale import AssemblyScales, wire
from app.modules.inventory.contracts_assembly_scale import AssemblyStationPolicy, AssemblySkuPolicy, AssemblySessionOpen, AssemblyStepOpen, AssemblyCapture
from app.modules.inventory.contracts_stock import StockCommand
from app.services.case_pick_service import CasePickService
from app.schemas import CasePickTaskActionRequest

WARE, TASK, LINE = 6667491, 1031, 1035
OPERATOR, SENDER = "ASM15.OP1031", "ASM15.GW1031"
DEVICE, SESSION, STEP, OPERATION = "ASM15.CASE1031", "ASM15.S1031", "ASM15.T1031", "ASM15.PICK1031"
ARTICLE, SOURCE_CELL, LOT = "QNATIVED9A5C53B54", "QGd9a5c53b54", "FULL.QA:d9a5c53b54"
REPORT = ROOT / "reports/retailcase/2026-10-15/assembly-scale/native-acceptance.json"
NOTE = "SIMULATED_TEST_LABEL_NOT_PHYSICAL; TEST_FIXTURE_NOT_HARDWARE"


def stamp(value=None):
    return (value or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")


def save(report):
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")


def native(cursor, method, *arguments):
    output = cursor.var(oracledb.DB_TYPE_CLOB)
    cursor.callproc("RRL_ASSEMBLY_SCALE_API." + method, [*arguments, output])
    return read_oracle_json(output.getvalue())


def post(cursor, command):
    output = cursor.var(oracledb.DB_TYPE_CLOB)
    cursor.callproc("RRL_STOCK_POSTING_API.prepare_command", [command.canonical_json(), command.actor, output])
    if output.getvalue() is None:
        cursor.callproc("RRL_STOCK_POSTING_API.execute_prepared", [output])
    return read_oracle_json(output.getvalue())


def no_post(command):
    raise AssertionError("This script must never call a committing quantitative stock runner")


def snapshot(gateway):
    return dict(stock=gateway.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u order by CELL", {"u": LOT}),
        task=gateway.fetch_all("select CASE_PICK_TASK_ID,PICKED_QTY,STATUS,ASSIGNED_TO,CONTENT_VERSION,PALLET_TYPE_ID,SSCC,ASSIGNED_RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID,STARTED_AT,STARTED_AT_INSTANT,STARTED_SHIFT_TIME_ZONE from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t", {"t": TASK}),
        line=gateway.fetch_all("select PICKED_QTY,STATUS from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:l", {"l": LINE}))


def stage(gateway, report):
    assert not REPORT.exists(), "Use existing retained fixture/report; do not blindly recreate"
    original = snapshot(gateway)
    assert original["task"][0]["status"] == "NEW" and original["task"][0]["content_version"] == 0
    assert sum(row["remain"] for row in original["stock"]) == 20
    assert sum(row["hard_reserved_base"] for row in original["stock"]) == 20
    report.update(original=original, fixture_note=NOTE, business_stock_committed=False, physical_verified=False)
    save(report)
    with stock_configuration_transaction(gateway, NOTE, "admin", "warehouse_settings_edit") as q:
        for actor, rights in ((OPERATOR, ("case_pick_execute", "case_pick_manage")), (SENDER, ("warehouse_scale_ingest",))):
            q.execute("select count(*) from RUSERS where ID=:a", a=actor)
            assert q.fetchone()[0] == 0, actor
            q.execute("insert into USER_GROUP(ID,NAME) values(:a,'ASM15 isolated DEV QA')", a=actor)
            for permission in rights:
                q.execute("insert into RIGHTS(RIGHT1,USER_GROUP,ID,DESCR) values(:r,:a,(select nvl(max(ID),0)+1 from RIGHTS),:n)", r=permission.upper(), a=actor, n=NOTE)
            password=secrets.token_urlsafe(32)
            private=ROOT / "runtime/assembly-qa-secrets.json"
            private.parent.mkdir(parents=True,exist_ok=True)
            saved=json.loads(private.read_text(encoding="utf-8"))if private.exists()else{}
            saved[actor]=password
            private.write_text(json.dumps(saved),encoding="utf-8")
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'ASM15 isolated DEV QA',:a,:w,0,0)", a=actor, p=password, w=WARE)
    report["actors_staged"] = True
    save(report)
    with oracle_connection() as connection:
        q = connection.cursor()
        command = StockCommand(f"ASM15.TYPE{TASK}", "CASE_PALLET_TYPE_CHANGE", "admin", (), {"case_task_id": TASK}, metadata={"expected_version": 0, "pallet_type_id": 32, "scan_container": original["task"][0]["sscc"], "reason": NOTE})
        try:
            result = post(q, command)
            assert result["stock_changed"] is False and result["status"] == "APPLIED", result
            connection.commit()  # Explicit root exception: canonical metadata-only command, no quantity change.
            report["type_change"] = result
            save(report)
        finally:
            connection.rollback()
            q.callproc("RRL_STOCK_POSTING_API.reset_connection")
    settings = ReceiptConfiguration(gateway)
    old = settings.get(WARE)
    report["warehouse_settings_before"] = old
    save(report)
    try:
        settings.save(WARE, {**old, "company_prefix": "900000", "extension_digit": 0}, "admin")
        labels = CaseLabels(gateway)
        label = labels.issue(TASK, CaseSsccLabelRequest(operation_id=f"ASM15.LABEL{TASK}", scan_container=original["task"][0]["sscc"], expected_content_version=1), OPERATOR)
        report["label"] = label
        save(report)
        report["simulated_label_confirmation"] = labels.confirm(TASK, label["sscc"], OPERATOR)
        save(report)
    finally:
        settings.save(WARE, old, "admin")
    if TASK==1032:
        prepare_second_tare(gateway, report)
    stage_measurements(gateway, report)


def stage_measurements(gateway, report):
    CasePickService(gateway).start_task(TASK, CasePickTaskActionRequest(actor=OPERATOR, reason=NOTE))
    configuration = WarehouseScaleConfiguration(warehouse_id=WARE, post_cell=SOURCE_CELL, sender_id=SENDER, expected_version=0,
        active=True, device_mode="TEST", basis="GROSS", capacity_kg="100", resolution_kg="0.001",
        calibration_ref="TEST_FIXTURE_NOT_HARDWARE:ASM15", calibrated_until=stamp(datetime.now(timezone.utc)+timedelta(days=1)))
    report["device"] = WarehouseScales(gateway).configure(DEVICE, configuration, "admin")
    save(report)
    assembly = AssemblyScales(gateway, no_post)
    report["station"] = assembly.station_policy(DEVICE, AssemblyStationPolicy(operation_id=f"ASM15.STATION{TASK}", expected_version=0,
        confirmation_mode="AUTO", max_session_seconds=28800, cumulative_tolerance_kg="0.002", active=True, reason=NOTE), "admin")
    if TASK==1031:
        report["sku_policy"] = assembly.sku_policy(AssemblySkuPolicy(operation_id=f"ASM15.SKU{TASK}", warehouse_id=WARE, article=ARTICLE,
            base_uom="EA", expected_version=0, min_unit_kg="0.99", max_unit_kg="1.01", min_delta_kg="0.01", tolerance_kg="0",
            active=True, evidence_reference="TEST_FIXTURE_NOT_HARDWARE:ASM15", reason=NOTE), "admin")
    else:
        policies=gateway.fetch_all("select VERSION_NO,MIN_UNIT_KG,MAX_UNIT_KG,MIN_DELTA_KG,TOLERANCE_KG,ACTIVE_FLAG from RRL_ASSEMBLY_SKU_POLICY where WARE_ID=:w and ARTICUL=:a",{"w":WARE,"a":ARTICLE})
        assert len(policies)==1 and policies[0]["version_no"]==1 and policies[0]["active_flag"]==1
        report["sku_policy"]={"reused_current_version":1,"no_policy_mutation":True}
    now = datetime.now(timezone.utc)
    tare_packet = WarehouseFinalScalePacket(device_id=DEVICE, capture_id=f"ASM15.TARE{TASK}", post_cell=SOURCE_CELL, case_task_id=TASK,
        expected_content_version=2, scan_container=report["label"]["sscc"], purpose="EMPTY_TARE", device_policy_version=1,
        calibration_ref=configuration.calibration_ref, unit="KG", basis="GROSS", preset_tare_kg="0", zero_confirmed=True,
        zero_check_kg="0", zero_check_at=stamp(now-timedelta(seconds=10)), measured_at=stamp(now),
        samples=[{"offset_ms":i*500,"weight_kg":"0.5"} for i in range(5)])
    report["tare"] = WarehouseScales(gateway).capture(tare_packet, SENDER)
    save(report)
    report["session"] = assembly.open_session(AssemblySessionOpen(session_id=SESSION, task_id=TASK, device_id=DEVICE,
        expected_content_version=2, tare_capture_key=report["tare"]["capture_key"], scan_container=report["label"]["sscc"]), OPERATOR)
    report["step"] = assembly.open_step(SESSION, AssemblyStepOpen(step_id=STEP, operation_id=OPERATION, case_line_id=LINE, quantity="1",
        scan_source_cell=SOURCE_CELL, scan_product=ARTICLE, scan_container=report["label"]["sscc"], expected_content_version=2, consent_to_auto=True), OPERATOR)
    save(report)
    if TASK==1032:
        report["staged_state"]=assembly.read_step(STEP,OPERATOR)
        assert report["staged_state"]["state"]=="WAITING_BEFORE"
        report["gateway_request"]=assembly.gateway_requests(DEVICE,SENDER)["items"][0]
        report["status"]="WAITING_REAL_ENCRYPTED_OPC_TEST_CLIENT"
        save(report)
        return
    for phase, weight in (("BEFORE", "0.5"), ("AFTER", "1.5")):
        time.sleep(2.1)  # Stable series is strictly after step/previous measured window, no database transaction held.
        request = assembly.gateway_requests(DEVICE, SENDER)["items"][0]
        assert request["phase"] == phase
        packet = AssemblyCapture(session_id=SESSION, step_id=STEP, capture_id=request["capture_id"], phase=phase, device_id=DEVICE,
            device_policy_version=1, calibration_ref=configuration.calibration_ref, unit="KG", basis="GROSS", preset_tare_kg="0",
            tare_mode_clear=True, quality_confirmed=True, measured_at=stamp(), samples=[{"offset_ms":i*500,"weight_kg":weight}for i in range(5)])
        with gateway.transaction("ASM15 immutable TEST series only; no stock runner") as q:
            report[phase] = native(q, "capture", wire(packet), SENDER)
        report[phase+"_packet"] = packet.model_dump()
        save(report)
    report["staged_state"] = assembly.read_step(STEP, OPERATOR)
    assert report["staged_state"]["state"] == "READY"
    save(report)



def approved_tare_command(command):
    with oracle_connection() as connection:
        q = connection.cursor()
        try:
            result = post(q, command)
            assert result["goods_stock_changed"] is False, result
            connection.commit()  # Explicit root-approved isolated TEST tare only; never goods CASE pick.
            return result
        finally:
            connection.rollback()
            q.callproc("RRL_STOCK_POSTING_API.reset_connection")


def resume(gateway, report):
    assert report["fixture_note"] == NOTE and report["label"]["sscc"] == "090000000000006010"
    current = snapshot(gateway)
    assert current["stock"] == report["original"]["stock"]
    assert current["task"][0]["status"] == "NEW" and current["task"][0]["content_version"] == 2
    rows = gateway.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32", {"w": WARE})
    assert not rows, "Initial TEST type32 balance must be absent/zero"
    report["tare_count_authorization"] = "Root explicit simulated observed TEST type32 count1 then nativeBOOK, finally cancel/count0; no hardware/goods claim"
    report["simulated_tare_count"] = approved_tare_command(StockCommand("ASM15.TARECOUNT1031", "TARE_COUNT", "admin", (), {}, metadata={
        "owner_ware_id":WARE,"pallet_type_id":32,"condition":"GOOD","observed_quantity":"1","expected_version":0,
        "reason":NOTE,"decision_reference":"TEST_FIXTURE_NOT_HARDWARE:ASM15"}))
    save(report)
    report["tare_booking"] = approved_tare_command(StockCommand("ASM15.TAREBOOK1031", "TARE_BOOK", "admin", (), {"place_kind":"CASE","place_id":str(TASK)}, metadata={"pallet_type_id":32,"expected_warehouse_id":WARE}))
    save(report)
    stage_measurements(gateway, report)




def prepare_second_tare(gateway, report):
    rows=gateway.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY,BALANCE_VERSION from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32",{"w":WARE})
    assert len(rows)==1 and (rows[0]["physical_qty"],rows[0]["assembly_qty"],rows[0]["available_qty"])==(1,1,0)
    held=gateway.fetch_all("select OPERATION_ID,PLACE_ID from RRL_TARE_BOOK where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32 and STATUS='HELD'",{"w":WARE})
    assert held==[{"operation_id":"ASM15.TAREBOOK1031","place_id":"1031"}],held
    report["tare_count_authorization"]="Root explicit second TEST type32 count1->2 for isolated1032 OPC discrepancy; no goods or hardware claim"
    report["simulated_tare_count"]=approved_tare_command(StockCommand("ASM15.TARECOUNT1032","TARE_COUNT","admin",(),{},metadata={"owner_ware_id":WARE,"pallet_type_id":32,"condition":"GOOD","observed_quantity":"2","expected_version":int(rows[0]["balance_version"]),"reason":NOTE,"decision_reference":"TEST_FIXTURE_NOT_HARDWARE:ASM15"}))
    save(report)
    report["tare_booking"]=approved_tare_command(StockCommand("ASM15.TAREBOOK1032","TARE_BOOK","admin",(),{"place_kind":"CASE","place_id":"1032"},metadata={"pallet_type_id":32,"expected_warehouse_id":WARE}))
    save(report)


def select_second_fixture():
    global TASK,LINE,OPERATOR,SENDER,DEVICE,SESSION,STEP,OPERATION,REPORT
    TASK,LINE=1032,1036
    OPERATOR,SENDER="ASM15.OP1032","ASM15.GW1032"
    DEVICE,SESSION,STEP,OPERATION="ASM15.CASE1032","ASM15.S1032","ASM15.T1032","ASM15.PICK1032"
    REPORT=ROOT / "reports/retailcase/2026-10-15/assembly-scale/opc-fixture.json"

def expect_refusal(cursor, procedure, arguments, marker):
    try:
        cursor.callproc(procedure, arguments)
    except oracledb.DatabaseError as error:
        assert marker in str(error), (marker, str(error))
        return marker
    raise AssertionError("Expected refusal: " + marker)


def accept(gateway, report):
    assembly = AssemblyScales(gateway, no_post)
    before = snapshot(gateway)
    with gateway.transaction("ASM15 current persisted operator command READ ONLY") as q:
        q.execute("set transaction read only")
        context = native(q, "posting_request", STEP, SENDER)
    assert context["eligible"] is True
    c = context["command"]
    command = StockCommand(c["operation_id"], "CASE_PICK_CONFIRM", c["actor"], (), c["source"], metadata=c["metadata"])
    assert command.actor == OPERATOR and command.actor != SENDER
    with oracle_connection() as connection:
        q = connection.cursor()
        try:
            result = post(q, command)
            q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c", u=LOT, c=SOURCE_CELL)
            assert q.fetchone() == (19,19)
            q.execute("select STATE from RRL_ASSEMBLY_STEP where STEP_ID=:s", s=STEP)
            assert q.fetchone() == ("APPLIED",)
            q.execute("select count(*)from RRL_ASSEMBLY_STEP_USE where STEP_ID=:s and STOCK_OPERATION_ID=:o and OPERATOR_ID=:a",s=STEP,o=OPERATION,a=OPERATOR)
            assert q.fetchone()[0] == 1
            q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:o", o=OPERATION)
            event_count=q.fetchone()[0]
            assert event_count>0
            q.execute("select count(*)from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:o",o=result["outbox_id"])
            assert q.fetchone()[0]==1
            report["positive_canonical_rollback"]={"result":result,"during_source":[19,19],"stock_events":event_count,"use_count":1,"business_actor":OPERATOR,"api_sender":SENDER}
        finally:
            connection.rollback()
            q.callproc("RRL_STOCK_POSTING_API.reset_connection")
    assert snapshot(gateway)==before
    for table,key in (("RRL_EVENTS","OPERATION_ID"),("RRL_STOCK_OPERATION","OPERATION_ID"),("RRL_ASSEMBLY_STEP_USE","STOCK_OPERATION_ID")):
        assert gateway.fetch_all("select count(*) N from "+table+" where "+key+"=:o",{"o":OPERATION})[0]["n"]==0, table
    assert gateway.fetch_all("select count(*) N from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:o",{"o":result["outbox_id"]})[0]["n"]==0
    assert gateway.fetch_all("select count(*) N from RRL_PALLETS where CREATED_BY_STOCK_OP=:o",{"o":OPERATION})[0]["n"]==0
    assert assembly.read_step(STEP,OPERATOR)["state"]=="READY"
    report["positive_canonical_rollback"]["after_source_task_line_unchanged"]=True
    report["positive_canonical_rollback"]["scoped_events_outbox_operation_newlot_use_absent"]=True
    save(report)
    checks=[]
    with oracle_connection() as connection:
        q=connection.cursor()
        try:
            output=q.var(oracledb.DB_TYPE_CLOB)
            packet=json.dumps(report["AFTER_packet"],ensure_ascii=True,sort_keys=True,separators=(",",":"))
            assert native(q,"capture",packet,SENDER)==report["AFTER"]
            changed=json.loads(packet);changed["samples"][0]["weight_kg"]="1.501"
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.capture",[json.dumps(changed),SENDER,output],"ASSEMBLY_CAPTURE_PAYLOAD_CONFLICT"))
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.finish",[SESSION,'{"final_capture_key":null}',OPERATOR,output],"ASSEMBLY_FINAL_CAPTURE_KEY_REQUIRED"))
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.posting_request",[STEP,None,output],"ASSEMBLY_SESSION_CALLER_REQUIRED"))
            changed=json.loads(command.canonical_json());changed["source"]["case_line_id"]=None
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.assert_post",[json.dumps(changed),0],"ASSEMBLY_POST_SOURCE_POLICY_CONFLICT"))
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.assert_post",[command.canonical_json(),None],"ASSEMBLY_POST_SOURCE_POLICY_CONFLICT"))
            q.execute("update RUSERS set DELETED=1 where ID=:a",a=OPERATOR)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.assert_post",[command.canonical_json(),0],"CASE_ACTIVE_USER_REQUIRED"))
        finally:
            connection.rollback()
    assert snapshot(gateway)==before
    assert gateway.fetch_all("select DELETED from RUSERS where ID=:a",{"a":OPERATOR})[0]["deleted"]==0
    report["negative_checks"]=checks
    report["status"]="NATIVE_POSITIVE_AND_CORE_GUARDS_PASS_MORE_ACCEPTANCE_OPEN"
    report["remaining_READY"]=True
    save(report)



def concurrency(gateway, report):
    assembly=AssemblyScales(gateway,no_post)
    before=snapshot(gateway)
    with gateway.transaction("ASM15 native concurrency stored command")as q:
        q.execute("set transaction read only")
        context=native(q,"posting_request",STEP,SENDER)
    c=context["command"]
    command=StockCommand(c["operation_id"],"CASE_PICK_CONFIRM",c["actor"],(),c["source"],metadata=c["metadata"])
    started=threading.Event()
    outcome=[]
    packet=json.dumps(report["AFTER_packet"],sort_keys=True,separators=(",",":"),ensure_ascii=True)
    request=AssemblyStepOpen(step_id="ASM15.CONCURRENCY1031",operation_id="ASM15.CONCURRENCY.PICK1031",case_line_id=LINE,quantity="1",scan_source_cell=SOURCE_CELL,scan_product=ARTICLE,scan_container=report["label"]["sscc"],expected_content_version=2,consent_to_auto=True)
    def concurrent_open():
        with oracle_connection()as other:
            q=other.cursor()
            try:
                started.set()
                native(q,"open_step",SESSION,wire(request),OPERATOR)
                outcome.append("UNEXPECTED_ACCEPT")
            except oracledb.DatabaseError as error:
                outcome.append(str(error))
            finally:other.rollback()
    with oracle_connection()as connection:
        q=connection.cursor()
        thread=None
        try:
            post(q,command)
            thread=threading.Thread(target=concurrent_open,daemon=True)
            thread.start()
            assert started.wait(5)
            time.sleep(0.25)
            assert thread.is_alive(),outcome
            with oracle_connection()as read_connection:
                replay=native(read_connection.cursor(),"capture",packet,SENDER)
                assert replay==report["AFTER"]
                read_connection.rollback()
        finally:
            connection.rollback()
            q.callproc("RRL_STOCK_POSTING_API.reset_connection")
        thread.join(12)
        assert not thread.is_alive(),"Native metadata waiter did not finish after stock rollback"
    assert len(outcome)==1 and "ASSEMBLY_PREVIOUS_STEP_UNRESOLVED"in outcome[0],outcome
    assert "ORA-00060"not in outcome[0]
    assert snapshot(gateway)==before
    assert assembly.read_step(STEP,OPERATOR)["state"]=="READY"
    report["concurrency"]={"claim_holds_stock_transaction":True,"parallel_open_waits_then_current_unresolved_guard":True,"exact_AFTER_replay_during_claim":"ORIGINAL_ACK","deadlock":False,"all_stock_rolled_back":True}
    save(report)



def policy_guards(gateway, report):
    policy=AssemblyStationPolicy(operation_id="ASM15.POLICY.GUARD",expected_version=1,confirmation_mode="AUTO",max_session_seconds=28800,cumulative_tolerance_kg="0.002",active=True,reason=NOTE)
    sku=AssemblySkuPolicy(operation_id="ASM15.SKU.GUARD",warehouse_id=WARE,article=ARTICLE,base_uom="EA",expected_version=1,min_unit_kg="0.99",max_unit_kg="1.01",min_delta_kg="0.01",tolerance_kg="0",active=True,evidence_reference="TEST_FIXTURE_NOT_HARDWARE:ASM15",reason=NOTE)
    checks=[]
    with oracle_connection()as connection:
        q=connection.cursor()
        try:
            # Acquire CONFIG before rights-revision DML, matching canonical order. All temporary.
            q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
            q.execute("insert into RIGHTS(RIGHT1,USER_GROUP,ID,DESCR)values('WAREHOUSE_SETTINGS_EDIT',:a,(select nvl(max(ID),0)+1 from RIGHTS),'ASM15 callerrollback config guard')",a=OPERATOR)
            q.callproc("RRL_STOCK_CONFIG_API.end_change")
            result=native(q,"station_policy",DEVICE,wire(policy),OPERATOR)
            assert result["version"]==2 and native(q,"station_policy",DEVICE,wire(policy),OPERATOR)==result
            output=q.var(oracledb.DB_TYPE_CLOB)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.station_policy",["ASM15.CASE1032",wire(policy),OPERATOR,output],"ASSEMBLY_POLICY_OPERATION_CONFLICT"))
            sku_result=native(q,"sku_policy",wire(sku),OPERATOR)
            assert sku_result["version"]==2 and native(q,"sku_policy",wire(sku),OPERATOR)==sku_result
            q.execute("update RUSERS set WARE_ID=7065498 where ID=:a",a=OPERATOR)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.station_policy",[DEVICE,wire(policy),OPERATOR,output],"ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED"))
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.sku_policy",[wire(sku),OPERATOR,output],"ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED"))
            q.execute("update RUSERS set WARE_ID=:w,DELETED=1 where ID=:a",w=WARE,a=OPERATOR)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.station_policy",[DEVICE,wire(policy),OPERATOR,output],"ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED"))
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.sku_policy",[wire(sku),OPERATOR,output],"ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED"))
        finally:
            connection.rollback()
            q.callproc("RRL_STOCK_CONFIG_API.end_change")
    row=gateway.fetch_all("select WARE_ID,DELETED from RUSERS where ID=:a",{"a":OPERATOR})[0]
    assert row=={"ware_id":WARE,"deleted":0}
    assert gateway.fetch_all("select count(*)N from RIGHTS where USER_GROUP=:a and upper(RIGHT1)='WAREHOUSE_SETTINGS_EDIT'",{"a":OPERATOR})[0]["n"]==0
    assert gateway.fetch_all("select VERSION_NO from RRL_ASSEMBLY_STATION where DEVICE_ID=:d",{"d":DEVICE})[0]["version_no"]==1
    assert gateway.fetch_all("select VERSION_NO from RRL_ASSEMBLY_SKU_POLICY where WARE_ID=:w and ARTICUL=:a",{"w":WARE,"a":ARTICLE})[0]["version_no"]==1
    report["policy_guards"]={"station_and_sku_exact_receipts":"ORIGINAL","other_station_same_op":"CONFLICT","refusals":checks,"all_metadata_rolled_back":True}
    save(report)



def packet_contracts(gateway, report):
    now=datetime.now(timezone.utc)
    legacy={"unit":"KG","basis":"GROSS","preset_tare_kg":"0","zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=10)),"measured_at":stamp(now),"samples":[{"offset_ms":i*500,"weight_kg":"0.5"}for i in range(5)]}
    series={k:v for k,v in legacy.items()if not k.startswith("zero_")}
    series.update(tare_mode_clear=True,quality_confirmed=True)
    checks=[]
    with oracle_connection()as connection:
        q=connection.cursor()
        def validate(body,old=False):
            args=[json.dumps(body),100,0.001]
            if old:args += ["GROSS","weight_kg"]
            result=q.callfunc("RRL_SCALE_PACKET_READ."+("validate_json"if old else"validate_series_json"),oracledb.DB_TYPE_CLOB,args)
            return read_oracle_json(result)
        try:
            assert validate(legacy,True)["weight_kg"]=="0.5"
            assert validate(series)["weight_kg"]=="0.5"
            vectors=[({**legacy,"zero_confirmed":False},True,"SCALE_ZERO_CONFIRMATION_REQUIRED"),
                ({**legacy,"zero_check_at":stamp(now-timedelta(seconds=601))},True,"SCALE_FRESH_ZERO_AND_MEASUREMENT_REQUIRED"),
                ({**series,"quality_confirmed":None},False,"ASSEMBLY_GROSS_QUALITY_NO_TARE_REQUIRED"),
                ({**series,"tare_mode_clear":False},False,"ASSEMBLY_GROSS_QUALITY_NO_TARE_REQUIRED"),
                ({**series,"basis":"NET"},False,"ASSEMBLY_GROSS_QUALITY_NO_TARE_REQUIRED"),
                ({k:v for k,v in series.items()if k!="quality_confirmed"},False,"ASSEMBLY_GROSS_QUALITY_NO_TARE_REQUIRED"),
                ({**series,"samples":[*series["samples"][:-1],{"offset_ms":2000,"weight_kg":"0.51"}]},False,"SCALE_STABLE_WINDOW_REQUIRED")]
            for body,old,marker in vectors:
                try:validate(body,old)
                except oracledb.DatabaseError as error:assert marker in str(error),(marker,str(error))
                else:raise AssertionError(marker)
                checks.append(marker)
        finally:connection.rollback()
    report["pure_packet_native"]={"legacy_zero_valid":"PASS","legacy_false_or_expired_zero":"DENIED","series_initial_zero_not_fabricated":True,"series_valid":"PASS","refusals":checks,"all_input_observations":"TEST_VECTORS_NOT_HARDWARE"}
    save(report)



def station_receipt_guards(gateway, report):
    actor="ASM15.CFG1031"
    with stock_configuration_transaction(gateway,"ASM15 isolated configuration guard actor","admin","warehouse_settings_edit")as q:
        q.execute("select count(*)from RUSERS where ID=:a",a=actor)
        existing=q.fetchone()[0]
        if existing==0:
            q.execute("insert into USER_GROUP(ID,NAME)values(:a,'ASM15 policy guard QA')",a=actor)
            q.execute("insert into RIGHTS(RIGHT1,USER_GROUP,ID,DESCR)values('WAREHOUSE_SETTINGS_EDIT',:a,(select nvl(max(ID),0)+1 from RIGHTS),'ASM15 policy receipts')",a=actor)
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'ASM15 policy guard QA',:a,:w,0,0)",a=actor,p=secrets.token_urlsafe(32),w=WARE)
        else:
            assert existing==1
            q.execute("select USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:a",a=actor)
            assert q.fetchone()==(actor,WARE,1)
            q.execute("update RUSERS set DELETED=0 where ID=:a",a=actor)
    assembly=AssemblyScales(gateway,no_post)
    body=AssemblyStationPolicy(operation_id="ASM15.STATION.RECEIPT1031",expected_version=1,confirmation_mode="AUTO",max_session_seconds=28800,cumulative_tolerance_kg="0.002",active=True,reason=NOTE)
    result=assembly.station_policy(DEVICE,body,actor)
    assert result["version"]==2 and assembly.station_policy(DEVICE,body,actor)==result
    checks=[]
    with oracle_connection()as con:
        q=con.cursor()
        try:
            output=q.var(oracledb.DB_TYPE_CLOB)
            checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.station_policy",["ASM15.CASE1032",wire(body),actor,output],"ASSEMBLY_POLICY_OPERATION_CONFLICT"))
        finally:con.rollback()
    try:
        with stock_configuration_transaction(gateway,"ASM15 configuration actor foreign scope","admin","warehouse_settings_edit")as q:
            q.execute("update RUSERS set WARE_ID=7065498 where ID=:a",a=actor)
        with oracle_connection()as con:
            try:checks.append(expect_refusal(con.cursor(),"RRL_ASSEMBLY_SCALE_API.station_policy",[DEVICE,wire(body),actor,con.cursor().var(oracledb.DB_TYPE_CLOB)],"ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED"))
            finally:con.rollback()
        with stock_configuration_transaction(gateway,"ASM15 configuration actor revoke","admin","warehouse_settings_edit")as q:
            q.execute("update RUSERS set WARE_ID=:w,DELETED=1 where ID=:a",a=actor,w=WARE)
        with oracle_connection()as con:
            try:checks.append(expect_refusal(con.cursor(),"RRL_ASSEMBLY_SCALE_API.station_policy",[DEVICE,wire(body),actor,con.cursor().var(oracledb.DB_TYPE_CLOB)],"CONFIGURATION_FORBIDDEN"))
            finally:con.rollback()
    finally:
        with stock_configuration_transaction(gateway,"ASM15 retain retired config identity","admin","warehouse_settings_edit")as q:
            q.execute("update RUSERS set WARE_ID=:w,DELETED=1 where ID=:a",a=actor,w=WARE)
    report["station_receipt_guards"]={"actor":actor,"exact_saved_receipt":result,"refusals":checks,"version_history":"v1->2 identical values retained","config_actor_retired":True,"shared_sku_version":"UNCHANGED_1"}
    save(report)


def retire_first(gateway, report):
    from app.modules.inventory.infrastructure.metadata_transactions import receipt_task_metadata
    original=report["original"]["task"][0]
    with receipt_task_metadata(gateway,"ASM15 restore only original QA CASE assignment/start fields","admin","case_pick_manage")as q:
        q.execute("select PICKED_QTY,CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t for update",t=TASK)
        row=q.fetchone()
        assert row[0]==0 and row[1]==2 and row[2]==report["label"]["sscc"]
        q.execute("update RRL_CASE_PICK_TASK set STATUS='NEW',ASSIGNED_TO=null,ASSIGNED_RESOURCE_ID=null,RESOURCE_SESSION_ID=null,EQUIPMENT_ID=null where CASE_PICK_TASK_ID=:t",t=TASK)
    report["book_cancel"]=approved_tare_command(StockCommand(f"ASM15.TARECANCEL{TASK}","TARE_BOOK_CANCEL","admin",(),{"booking_operation_id":f"ASM15.TAREBOOK{TASK}"}))
    save(report)
    with oracle_connection()as con:
        q=con.cursor()
        try:
            result=post(q,StockCommand(f"ASM15.TYPERESTORE{TASK}","CASE_PALLET_TYPE_CHANGE","admin",(),{"case_task_id":TASK},metadata={"expected_version":2,"pallet_type_id":original["pallet_type_id"],"scan_container":report["label"]["sscc"],"reason":NOTE+" restore original empty type"}))
            assert result["stock_changed"]is False
            con.commit()
            report["type_restore"]=result
        except oracledb.DatabaseError as error:
            report["type_restore"]={"native_refusal":str(error),"no_bypass":True}
        finally:
            con.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
    configuration=WarehouseScaleConfiguration(warehouse_id=WARE,post_cell=SOURCE_CELL,sender_id=SENDER,expected_version=1,active=False,device_mode="TEST",basis="GROSS",capacity_kg="100",resolution_kg="0.001",calibration_ref="TEST_FIXTURE_NOT_HARDWARE:ASM15",calibrated_until=stamp(datetime.now(timezone.utc)+timedelta(days=1)))
    report["device_retire"]=WarehouseScales(gateway).configure(DEVICE,configuration,"admin")
    with stock_configuration_transaction(gateway,"ASM15 retire first dedicated QA identities","admin","warehouse_settings_edit")as q:
        q.execute("update RUSERS set DELETED=1 where ID in(:a,:b)",a=OPERATOR,b=SENDER)
    current=snapshot(gateway)
    assert current["stock"]==report["original"]["stock"] and current["line"]==report["original"]["line"]
    assert current["task"][0]["status"]=="NEW" and current["task"][0]["assigned_to"]is None
    assert current["task"][0]["sscc"]==report["label"]["sscc"]
    report[f"cleanup{TASK}"]={"current":current,"stock_and_line_exact_original":True,"new_sscc_retained":True,"operator_and_sender_retired":True,"assembly_history_preserved":"Existing step/session and evidence unchanged; inactive device+retired actors/current version change forbid posting","shared_tare_count_zero":"DEFERRED until1032 booking released"}
    report["status"]="NATIVE_ACCEPTANCE_LIMITED_PASS_1031_RETIRED_1032_RECOVERY_PENDING"
    save(report)



def sku_receipt_guards(gateway, report):
    actor="ASM15.CFG1031"
    with stock_configuration_transaction(gateway,"ASM15 bounded SKU configuration receipt actor","admin","warehouse_settings_edit")as q:
        q.execute("select USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:a",a=actor)
        assert q.fetchone()==(actor,WARE,1)
        q.execute("update RUSERS set DELETED=0 where ID=:a",a=actor)
    service=AssemblyScales(gateway,no_post)
    body=AssemblySkuPolicy(operation_id="ASM15.SKU.RECEIPT",warehouse_id=WARE,article=ARTICLE,base_uom="EA",expected_version=1,min_unit_kg="0.99",max_unit_kg="1.01",min_delta_kg="0.01",tolerance_kg="0",active=True,evidence_reference="TEST_FIXTURE_NOT_HARDWARE:ASM15",reason=NOTE)
    checks=[]
    try:
        result=service.sku_policy(body,actor)
        assert result["version"]==2 and service.sku_policy(body,actor)==result
        with stock_configuration_transaction(gateway,"ASM15 SKU foreign configuration actor","admin","warehouse_settings_edit")as q:
            q.execute("update RUSERS set WARE_ID=7065498 where ID=:a",a=actor)
        with oracle_connection()as con:
            q=con.cursor()
            try:checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.sku_policy",[wire(body),actor,q.var(oracledb.DB_TYPE_CLOB)],"ASSEMBLY_CURRENT_CONFIGURATION_SCOPE_REQUIRED"))
            finally:con.rollback()
        with stock_configuration_transaction(gateway,"ASM15 SKU revoked configuration actor","admin","warehouse_settings_edit")as q:
            q.execute("update RUSERS set WARE_ID=:w,DELETED=1 where ID=:a",a=actor,w=WARE)
        with oracle_connection()as con:
            q=con.cursor()
            try:checks.append(expect_refusal(q,"RRL_ASSEMBLY_SCALE_API.sku_policy",[wire(body),actor,q.var(oracledb.DB_TYPE_CLOB)],"CONFIGURATION_FORBIDDEN"))
            finally:con.rollback()
        report["sku_receipt_guards"]={"exact_receipt":result,"refusals":checks,"version_history":"v1->2 identical TEST configuration values; after recovery1032 completed"}
        save(report)
    finally:
        with stock_configuration_transaction(gateway,"ASM15 retire SKU configuration actor","admin","warehouse_settings_edit")as q:
            q.execute("update RUSERS set WARE_ID=:w,DELETED=1 where ID=:a",a=actor,w=WARE)


def retire_second(gateway, report):
    retire_first(gateway,report)
    rows=gateway.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY,BALANCE_VERSION from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32",{"w":WARE})
    assert len(rows)==1 and(rows[0]["physical_qty"],rows[0]["assembly_qty"],rows[0]["available_qty"])==(2,0,2)
    report["final_test_tare_count0"]=approved_tare_command(StockCommand("ASM15.TARECOUNT.RESTORE0","TARE_COUNT","admin",(),{},metadata={"owner_ware_id":WARE,"pallet_type_id":32,"condition":"GOOD","observed_quantity":"0","expected_version":int(rows[0]["balance_version"]),"reason":NOTE+" restore initial TEST quantity0","decision_reference":"TEST_FIXTURE_NOT_HARDWARE:ASM15"}))
    current=gateway.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32",{"w":WARE})
    assert current==[{"physical_qty":0,"assembly_qty":0,"available_qty":0}]
    assert not gateway.fetch_all("select OPERATION_ID from RRL_TARE_BOOK where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32 and STATUS='HELD'",{"w":WARE})
    report["cleanup1032"]["shared_test_tare_count_zero"]="RESTORED through canonical owner; balance/journal/version history retained"
    report["status"]="NATIVE_AND_OPC_RECOVERY_PASS_ALL_QA_RETIRED"
    save(report)
    private=ROOT/"runtime/assembly-qa-secrets.json"
    if private.exists():
        saved=json.loads(private.read_text(encoding="utf-8"))
        for actor in("ASM15.OP1031","ASM15.GW1031","ASM15.OP1032","ASM15.GW1032"):saved.pop(actor,None)
        if saved:private.write_text(json.dumps(saved),encoding="utf-8")
        else:private.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-approved-test-fixture", action="store_true")
    parser.add_argument("--resume-approved-tare-simulation", action="store_true")
    parser.add_argument("--accept-native-rollback", action="store_true")
    parser.add_argument("--stage-approved-opc-fixture", action="store_true")
    parser.add_argument("--concurrency-native-rollback", action="store_true")
    parser.add_argument("--policy-native-rollback", action="store_true")
    parser.add_argument("--packet-contracts", action="store_true")
    parser.add_argument("--station-receipts", action="store_true")
    parser.add_argument("--retire-first", action="store_true")
    parser.add_argument("--sku-receipts", action="store_true")
    parser.add_argument("--retire-second", action="store_true")
    args = parser.parse_args()
    gateway = OracleGateway()
    if args.sku_receipts:
        report=json.loads(REPORT.read_text(encoding="utf-8"))
        sku_receipt_guards(gateway,report)
    elif args.retire_second:
        select_second_fixture()
        report=json.loads(REPORT.read_text(encoding="utf-8"))
        retire_second(gateway,report)
    elif args.station_receipts:
        report=json.loads(REPORT.read_text(encoding="utf-8"))
        station_receipt_guards(gateway,report)
    elif args.retire_first:
        report=json.loads(REPORT.read_text(encoding="utf-8"))
        retire_first(gateway,report)
    elif args.packet_contracts:
        report=json.loads(REPORT.read_text(encoding="utf-8"))
        packet_contracts(gateway,report)
    elif args.policy_native_rollback:
        report=json.loads(REPORT.read_text(encoding="utf-8"))
        policy_guards(gateway,report)
    elif args.concurrency_native_rollback:
        report=json.loads(REPORT.read_text(encoding="utf-8"))
        concurrency(gateway,report)
    elif args.stage_approved_opc_fixture:
        select_second_fixture()
        report={"status":"STAGING","fixture":{"task":TASK,"line":LINE,"ware":WARE,"operator":OPERATOR,"sender":SENDER,"device":DEVICE}}
        stage(gateway,report)
    elif args.accept_native_rollback:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        accept(gateway, report)
    elif args.resume_approved_tare_simulation:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        resume(gateway, report)
    else:
        assert args.stage_approved_test_fixture, "Explicit approved staging flag required"
        report = {"status":"STAGING", "fixture":{"task":TASK,"line":LINE,"ware":WARE,"operator":OPERATOR,"sender":SENDER,"device":DEVICE}}
        stage(gateway, report)
    print(json.dumps({"status":"READY_METADATA_ONLY", "report":str(REPORT), "physical_verified":False}))


if __name__ == "__main__":
    main()
