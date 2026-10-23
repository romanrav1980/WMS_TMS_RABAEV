"""Recover the completed own move after later hold/stock changes; recheck current grants."""
import json
from pathlib import Path
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "tests/tradecase")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http, expect, CALLS
import oracledb

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-23/T11"
proof = json.loads(OUT.joinpath("quality-release-scope.json").read_text(encoding="utf-8"))
assert proof["status"] == "PASS"
ACTOR = proof["last_actor"]; assert ACTOR.startswith("QG23")
WARE, UID = 212476763, proof["pallet_uid"]
ASSIGNMENT = ACTOR + ".REPLAY." + uuid4().hex[:6]
BASE = f"/api/tradecase/warehouses/{WARE}"
report = dict(status="FAIL", checks=[], http=CALLS, fixture="Only the actor created by this current release test; original revoked assignment is not restored")
password = None; hold = None; version = None; created = False


def call(body, status=200):
    return expect(status, http("POST", BASE + "/exceptions/quarantine-moves", body, ACTOR, password))


def owner(version, view, operate):
    return expect(200, http("PUT", BASE + "/stock/owner-grants", dict(operation_id=ASSIGNMENT + "." + str(version), expected_version=version,
        username=ACTOR, owner_id="SNS", can_view=view, can_operate=operate, reason="Continue own completed-move replay acceptance"), "admin", "admin123"))["version"]


if __name__ == "__main__":
    try:
        with oracle_connection() as c:
            q = c.cursor(); q.execute("select PASS,WARE_ID,NAME,USER_GROUP,DELETED from RUSERS where ID=:a", a=ACTOR)
            row = q.fetchone(); assert row[1:] == (WARE, "Role-only quarantine QA", "TC03QA", 1)
            password = row[0]
            q.execute("update RUSERS set DELETED=0 where ID=:a and WARE_ID=:w", a=ACTOR, w=WARE)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:id,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Own current replay test',1)", id=ASSIGNMENT, a=ACTOR, w=str(WARE))
            q.execute("select VERSION_NO from RRL_TRADE_OWNER_GRANT where WARE_ID=:w and USERNAME=:a and OWNER_ID='SNS'", w=WARE, a=ACTOR); version = q.fetchone()[0]
            c.commit(); created = True
        version = owner(version, True, True)
        body = dict(operation_id=proof["quarantine"]["operation_id"], pallet_uid=UID, target_cell="Q23.25cadbfc", reason="Own release scope QA")
        original = call(body); assert original == proof["quarantine"]
        with oracle_connection() as c:
            q = c.cursor(); hold = int(q.callfunc("RRL_TRACEABILITY_API.create_quality_hold", oracledb.DB_TYPE_NUMBER,
                ["PALLET", UID, "QA_ARCHIVED_REPLAY", "Later hold on own already issued pallet", "admin"])); c.commit()
        assert call(body) == original
        report["checks"].append("Original receipt survives completed disposal and a later hold; no new physical effect")
        call(dict(body, reason="Changed original request"), 409)
        with oracle_connection() as c:
            q = c.cursor(); q.execute("delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:a and PERMISSION='quarantine_move'", a=ACTOR); assert q.rowcount == 1; c.commit()
        call(body, 403)
        with oracle_connection() as c:
            q = c.cursor(); q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'quarantine_move')", a=ACTOR); c.commit()
        assert call(body) == original
        version = owner(version, False, False); call(body, 403)
        version = owner(version, True, True)
        with oracle_connection() as c:
            q = c.cursor(); q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a", a=ASSIGNMENT); c.commit()
        call(body, 403)
        report["checks"].append("Changed body refused; move-right, owner and warehouse revocation deny archived replay; restored right recovers original receipt")
        with oracle_connection() as c:
            q = c.cursor(); q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:u", u=UID); assert q.fetchone() == (0, 0)
            q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'", o=body["operation_id"]); assert q.fetchone() == (1,)
        report["status"] = "PASS"
    finally:
        if created:
            if version is not None: version = owner(version, False, False)
            with oracle_connection() as c:
                q = c.cursor()
                if hold is not None: q.callproc("RRL_TRACEABILITY_API.release_quality_hold", [hold, "admin", "Own archived replay proof complete"])
                q.execute("merge into RRL_ACCESS_ROLE_RIGHT d using(select :a A,'quarantine_move'P from dual)s on(d.ROLE_ID=s.A and d.PERMISSION=s.P)when not matched then insert(ROLE_ID,PERMISSION)values(s.A,s.P)", a=ACTOR)
                q.execute("update RUSERS set DELETED=1 where ID=:a and WARE_ID=:w", a=ACTOR, w=WARE)
                q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a", a=ASSIGNMENT); c.commit()
            report["qa_retired_owner_revoked_hold_released"] = True
        OUT.joinpath("quarantine-replay-scope.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(dict(status=report["status"], groups=len(report["checks"]), calls=len(CALLS))))
