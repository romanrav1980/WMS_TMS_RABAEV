"""Role-only access to the completed own case; no new receipt or quantity command succeeds."""
import json
from pathlib import Path
import secrets
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "tests/tradecase")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http, CALLS

TAG, PASSWORD, WARE = "QS23" + uuid4().hex[:10], secrets.token_hex(24), 212476763
BASE = f"/api/tradecase/warehouses/{WARE}"
report = dict(status="FAIL", checks=[], http=CALLS)


def call(method, path, body=None, status=200, admin=False):
    code, result = http(method, path, body, "admin" if admin else TAG, "admin123" if admin else PASSWORD)
    assert code == status, (code, result)
    return result


def grant(version, view, operate):
    return call("PUT", BASE + "/stock/owner-grants", dict(operation_id=TAG + ".owner." + str(version), expected_version=version,
        username=TAG, owner_id="SNS", can_view=view, can_operate=operate, reason="Own quality scope acceptance"), admin=True)


if __name__ == "__main__":
    created = False; grant_version = None
    try:
        with oracle_connection() as c:
            q = c.cursor(); q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Quality scope QA','TC03QA',:w,0,1)", a=TAG, p=PASSWORD, w=WARE)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Quality scope QA',1,1)", a=TAG)
            for permission in ("tradecase_view", "tradecase_quality_control", "tradecase_quality_approve", "tradecase_quality_post"):
                q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)", a=TAG, p=permission)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Quality scope acceptance',1)", a=TAG, w=str(WARE))
            c.commit(); created = True
        detail = BASE + "/exceptions/cases/1"
        request = dict(operation_id=TAG + ".refused", case_id=1, expected_version=3)
        assert call("GET", BASE + "/exceptions")["cases"] == []
        call("GET", detail, status=404); call("POST", BASE + "/exceptions/write-offs", request, status=403)
        grant_version = grant(0, True, False)["version"]
        assert call("GET", detail)["state"] == "POSTED"
        call("POST", BASE + "/exceptions/write-offs", request, status=403)
        grant_version = grant(grant_version, True, True)["version"]
        refused = call("POST", BASE + "/exceptions/write-offs", request, status=409)
        assert "APPROVED_CASE_REQUIRED" in refused["detail"]["code"]
        call("POST", BASE + "/exceptions/write-offs", dict(request, operation_id="Q23.post.25cadbfc"), status=409)
        report["checks"].append("Role-only warehouse access; hidden owner conceals case, view-only cannot write, operate reaches closed-state refusal, other actor cannot replay")
        grant_version = grant(grant_version, False, False)["version"]
        call("GET", detail, status=404); call("POST", BASE + "/exceptions/write-offs", request, status=403)
        with oracle_connection() as c:
            q = c.cursor(); q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a", a=TAG); c.commit()
        call("GET", BASE + "/exceptions", status=403)
        call("POST", BASE + "/exceptions/write-offs", request, status=403)
        report["checks"].append("Owner and warehouse revocation remove access on the next request")
        report["status"] = "PASS"
    finally:
        if created:
            with oracle_connection() as c:
                q = c.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a", a=TAG)
                q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a", a=TAG); c.commit()
            report["qa_retired"] = True
        path = ROOT / "runtime/test-evidence/tradecase/2026-10-23/T11" / (TAG + ".json")
        path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(dict(status=report["status"], groups=len(report["checks"]), calls=len(CALLS), evidence=str(path))))
