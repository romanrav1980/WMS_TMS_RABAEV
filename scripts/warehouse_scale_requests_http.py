"""Actual HTTP on dedicated shared QA accounts; no new quantitative writes."""
import json
import sys
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from warehouse_scale_requests_fixture import REPORT,ACTOR,SENDER,PREFIX,WARE
ctx=json.loads(REPORT.read_text(encoding="utf-8-sig"))
secret=json.loads((ROOT/"runtime/warehouse-weigh-qa-secrets.json").read_text(encoding="utf-8"))
url="http://127.0.0.1:8088/api/inventory/warehouse-scales"
checks=[]
with httpx.Client(auth=(ACTOR,secret[ACTOR]),timeout=15)as operator,httpx.Client(auth=(SENDER,secret[SENDER]),timeout=15)as sender:
    status=operator.get(url+"/requests/"+ctx["empty_request_body"]["request_id"])
    assert status.status_code==200,status.text
    actual=status.json()
    assert actual["state"]=="CAPTURED"and actual["capture_key"]==ctx["empty_archive"]["capture_key"],actual
    assert actual["current_context"]=="STALE"and actual["admissible"]is False,actual
    checks.append("operator_no_admin_flag_reads_immutable_CAPTURED_with_STALE_context_after_actual_claim_start")
    replay=operator.post(url+"/requests",json=ctx["empty_request_body"])
    assert replay.status_code==200 and replay.json()==actual,(replay.status_code,replay.text)
    checks.append("exact_original_request_HTTP_replay_has_current_auth_and_historical_key")
    ack=sender.post(url+"/final-captures",json=ctx["empty_capture_body"],headers={"X-Scale-Protocol-Version":"1.0"})
    assert ack.status_code==200 and ack.json()==ctx["empty_archive"],(ack.status_code,ack.text)
    checks.append("late_historical_original_sender_exact_packet_returns_identical_native_ACK")
    devices=operator.get(url+"/devices",params=dict(case_task_id=ctx["case"],purpose="EMPTY_TARE"))
    assert devices.status_code==200,devices.text
    device=next(row for row in devices.json()["items"]if row["device_id"]==ctx["empty_request_body"]["device_id"])
    assert device["active"]is True and device["connectivity"]=="UNKNOWN",device
    checks.append("scoped_actual_device_catalog_active_calibration_and_UNKNOWN_connectivity")
    pending=sender.get(url+"/gateway/requests",params=dict(device_id=device["device_id"]))
    assert pending.status_code==200 and pending.json()["items"]==[],pending.text
    checks.append("dedicated_ingest_only_sender_can_poll_without_admin_shell_permission")
    blocked=operator.get(url+"/gateway/requests",params=dict(device_id=device["device_id"]))
    assert blocked.status_code==403,blocked.text
    checks.append("operator_cannot_impersonate_ingest_sender")
    claim=dict(claim_id=PREFIX+".EMPTY.C2",device_id=device["device_id"])
    lease=sender.post(url+"/gateway/requests/"+ctx["empty_request_body"]["request_id"]+"/claim",json=claim)
    assert lease.status_code==200 and lease.json()["claim_active"]is False and lease.json()["state"]=="CAPTURED",lease.text
    checks.append("captured_expired_exact_claim_HTTP_replay_never_renews_lease")
    bad_version=operator.post(url+"/requests",json=ctx["empty_request_body"],headers={"X-Scale-Protocol-Version":"2.0"})
    assert bad_version.status_code==422,bad_version.text
    checks.append("unsupported_protocol_rejected_before_native_mutation")
    for patch in(dict(weight_kg="10"),dict(actor="admin")):
        bad=operator.post(url+"/requests",json={**ctx["empty_request_body"],**patch})
        assert bad.status_code==422,bad.text
    checks.append("browser_mass_and_actor_fields_rejected")
    denied=operator.post(url+"/final-captures",json=ctx["empty_capture_body"])
    assert denied.status_code==403,denied.text
    checks.append("operator_cannot_post_equipment_packet")
    ingest_only=sender.post(url+"/requests",json={**ctx["empty_request_body"],"request_id":PREFIX+".UNAUTHORIZED"})
    assert ingest_only.status_code==403,ingest_only.text
    checks.append("sender_ingest_permission_does_not_grant_operator_measurement_intent")
result=dict(status="PASS",checks=checks,case=ctx["case"],historical_status=actual,original_native_ACK_unchanged=True,
            physical_hardware=False,new_goods_mutations=0,new_requests_created=0)
target=ROOT/"reports/retailcase/2026-10-15/warehouse-weigh-request/http.json"
target.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(dict(status="PASS",checks=len(checks),state=actual["state"],current_context=actual["current_context"])))
