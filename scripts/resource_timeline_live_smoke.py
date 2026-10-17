"""Isolated native role fixtures and live HTTP admission checks; no stock writes."""
import json
import re
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "api/wms_api_server"), str(ROOT / "scripts")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command, normalize


def main():
    gateway = OracleGateway()
    access = AccessMetadataService(gateway)
    prefix = "rtl" + uuid4().hex[:9]
    password = secrets.token_urlsafe(24)
    actor, role, assignment = prefix + "u", prefix + "r", prefix + "a"
    target = ROOT / "reports/retailcase/2026-10-15/resource-timeline"
    target.mkdir(parents=True, exist_ok=True)
    checks = []
    now = datetime.now(timezone.utc)
    params = {"warehouse_id": 6667491, "start_at": (now-timedelta(days=1)).isoformat(), "finish_at": (now+timedelta(days=1)).isoformat()}
    def command(kind, body):
        return access.command("admin", normalize(Command(operation_id=prefix+":"+uuid4().hex, command_type=kind, payload=body), "ACCESS"))
    try:
        with gateway.transaction("timeline.acceptance.fixture") as cur:
            cur.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Timeline fixture',:password,'NONE',1,0,1)", id=actor, password=password)
        command("ROLE_SAVE", dict(role_id=role, title="Timeline fixture", permissions=["resource_gantt_view"], active=True, expected_version=0))
        command("ASSIGN", dict(assignment_id=assignment, username=actor, role_id=role, scope_kind="WAREHOUSE", scope_id="6667491", membership="CURRENT", valid_from=(now-timedelta(minutes=1)).isoformat(), valid_until=(now+timedelta(hours=1)).isoformat(), reason="Isolated HTTP admission acceptance", expected_version=0))
        with httpx.Client(base_url="http://127.0.0.1:8088", timeout=30) as client:
            assert client.get("/api/resources/timeline", params=params).status_code == 401
            client.auth = (actor,password)
            first = client.get("/api/resources/timeline", params=params)
            assert first.status_code == 200, first.text[:300]
            assert all(source["status"] == "FORBIDDEN" for source in first.json()["sources"])
            assert not first.json()["resources"] and not first.json()["events"]
            nav=client.get("/api/access/workspaces")
            assert nav.status_code==200,nav.text[:300]
            assert [w["warehouse_id"] for w in nav.json()["warehouses"]]==[6667491]
            assert nav.json()["warehouses"][0]["capabilities"]["resource_timeline"] is True
            assert nav.json()["warehouses"][0]["capabilities"]["dispatch"] is False
            checks.append("native_workspace_navigation_scope_not_job_title")
            checks.append("timeline_right_does_not_grant_other_source_rights")
            foreign = client.get("/api/resources/timeline", params=params|{"warehouse_id":1})
            assert foreign.status_code == 403, foreign.text[:300]
            checks.append("native_assignment_other_warehouse_denied")
            command("ROLE_SAVE", dict(role_id=role,title="Timeline fixture",permissions=["resource_gantt_view","resource_management_view"],active=True,expected_version=1))
            registry = client.get("/api/resources/timeline",params=params)
            assert registry.status_code == 200, registry.text[:300]
            data = registry.json()
            assert any(lane["kind"] == "CASE_PICKER" for lane in data["resources"])
            assert all(lane["warehouse_id"]==6667491 and lane["availability"]=="UNKNOWN" for lane in data["resources"])
            assert all(source["status"]=="FORBIDDEN" for source in data["sources"] if source["source_id"]!="registry")
            checks.append("scoped_registry_real_picker_unknown_availability")
            assert client.get("/api/resources/timeline",params=params|{"start_at":"2026-10-15T01:00:00"}).status_code==422
            assert client.get("/api/resources/timeline",params=params|{"finish_at":(now+timedelta(days=10)).isoformat()}).status_code==422
            checks.append("naive_or_unbounded_window_rejected")
            command("REVOKE",dict(assignment_id=assignment,expected_version=1,reason="fixture revoke acceptance"))
            assert client.get("/api/resources/timeline",params=params).status_code==403
            assert client.get("/api/access/workspaces").json()["warehouses"]==[]
            checks.append("revoke_immediate_native_denial")
            basic=re.search(r'VITE_ADMIN_BASIC_AUTH=([^"\r\n]+)',(ROOT/"front.bat").read_text(encoding="utf-8-sig")).group(1)
            client.auth=tuple(basic.split(":",1))
            admin=client.get("/api/resources/timeline",params=params|{"warehouse_id":1})
            assert admin.status_code==200,admin.text[:300]
            result=admin.json()
            assert result["time_policy"]=="AWARE_ONLY_LEGACY_LOCAL_UNRESOLVED"
            assert all(event["time_status"]=="TIME_UNRESOLVED" for event in result["unscheduled"])
            assert all(source["observed_at"] for source in result["sources"])
            checks.append("admin_live_source_contract_aware_and_legacy_separated")
    finally:
        with gateway.transaction("timeline.acceptance.cleanup") as cur:
            cur.execute("delete from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:id",id=assignment)
            for table in ("RRL_ACCESS_ROLE_RIGHT","RRL_ACCESS_ROLE"):
                cur.execute("delete from "+table+" where ROLE_ID=:id",id=role)
            cur.execute("delete from RRL_ACCESS_AUDIT where OPERATION_ID like :prefix",prefix=prefix+":%")
            cur.execute("delete from RRL_PLATFORM_COMMAND where OPERATION_ID like :prefix",prefix=prefix+":%")
            cur.execute("delete from RUSERS where ID=:id",id=actor)
    report={"status":"PASS","checks":checks,"stock_effect":"NONE","fixture_cleaned":True}
    (target/"http-native.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report))


if __name__=="__main__":main()
