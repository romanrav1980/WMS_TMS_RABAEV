"""Compare exact task rows, scoped access and retirement after the admin SQL shortcut."""
import json
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.task_scoped_view import scoped_task_queue
from app.modules.inventory.infrastructure.task_view_predicate import task_view_predicate
from app.modules.inventory.contracts_task_read import TaskReadError

TAG, WARE = "QA23" + uuid4().hex[:10], 212476763
OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-23/T12"
old = (ROOT / "runtime/test-evidence/tradecase/2026-10-23/T11/slow-task-query.sql").read_text(encoding="utf-8")
start = old.index("((FROM_WARE_ID is not null")
end = old.index("\n                 order by", start)
new = old[:start] + "(" + task_view_predicate() + ")" + old[end:]
report = dict(status="FAIL", checks=[], timings=[])


def compare(actor):
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only")
        results = []
        for text in [old, new]:
            start = time.perf_counter(); q.execute(text, view_actor=actor, limit=500); rows = q.fetchall()
            report["timings"].append(dict(actor=actor, ms=round((time.perf_counter() - start) * 1000, 2), rows=len(rows)))
            results.append(rows)
        assert results[0] == results[1]
        return results[0]


if __name__ == "__main__":
    created = False
    try:
        with oracle_connection() as c:
            q = c.cursor()
            for actor, group in [(TAG, "TC03QA"), (TAG + "A", "GLOBAL_ADMIN")]:
                q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED)values(:a,:p,'Task ACL QA',:g,:w,0)", a=actor, p=secrets.token_hex(24), g=group, w=WARE)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Task ACL QA',1,1)", a=TAG)
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'warehouse_task_view')", a=TAG)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Task ACL equality',1)", a=TAG, w=str(WARE))
            c.commit(); created = True
        assert len(compare("admin")) == 500
        assert len(compare(TAG + "A")) == 500
        own = compare(TAG); assert own and all((r[13] in (None, WARE)) and (r[15] in (None, WARE)) for r in own)
        actual = scoped_task_queue(OracleGateway(), TAG, None, {"limit": 500}); assert len(actual) == len(own)
        report["checks"].append("Identical ordered rows for existing admin, fresh global admin and warehouse-only role")
        with oracle_connection() as c:
            q = c.cursor(); q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a", a=TAG)
            q.execute("update RUSERS set DELETED=1 where ID=:a", a=TAG + "A"); c.commit()
        assert compare(TAG) == [] and compare(TAG + "A") == []
        try:
            scoped_task_queue(OracleGateway(), TAG, None, {"limit": 500})
            raise AssertionError("Revoked viewer accepted")
        except TaskReadError:
            pass
        report["checks"].append("Role revocation and retired global admin deny the next read without a stale authorization cache")
        report["status"] = "PASS"
    finally:
        if created:
            with oracle_connection() as c:
                q = c.cursor(); q.execute("update RUSERS set DELETED=1 where ID in(:a,:b)", a=TAG, b=TAG + "A")
                q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a", a=TAG); c.commit()
            report["qa_retired"] = True
        OUT.joinpath("task-acl-live.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(dict(status=report["status"], checks=len(report["checks"]), timings=report["timings"])))
