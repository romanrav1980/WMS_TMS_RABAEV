"""Profile a new native wave on the retained, isolated second BOX receipt."""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
import live_factory_case as case
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-21/T12"
STATE = OUT / "profile-factory-state.json"
PROOF = ROOT / "runtime/test-evidence/tradecase/2026-10-21/T03/factory-box-222823304.json"


def snapshot():
    with oracle_connection() as conn:
        q = conn.cursor()
        q.execute("""select sql_id,plan_hash_value,sum(executions),sum(elapsed_time),sum(cpu_time),
            sum(buffer_gets),sum(disk_reads),sum(rows_processed),max(sql_text)
            from v$sql where parsing_schema_name=user and executions>0
            group by sql_id,plan_hash_value""")
        return {(r[0], r[1]): r for r in q}


def differences(before, after):
    rows = []
    for key, row in after.items():
        prior = before.get(key, (*key, 0, 0, 0, 0, 0, 0, ""))
        delta = [row[i] - prior[i] for i in range(2, 8)]
        if delta[0] > 0 and "from v$sql" not in row[8].lower():
            rows.append(dict(sql_id=key[0], plan_hash=key[1], executions=delta[0],
                             elapsed_ms=round(delta[1]/1000, 3), cpu_ms=round(delta[2]/1000, 3),
                             buffer_gets=delta[3], disk_reads=delta[4], rows=delta[5], sql=row[8]))
    return sorted(rows, key=lambda r: r["elapsed_ms"], reverse=True)


def configure():
    proof = json.loads(PROOF.read_text());f = proof["fixture"]
    assert proof["status"] == "PASS" and f["warehouse_id"] == 222823304
    assert f["tag"] == "c3ab08c4" and f["article"] == "TC03C3AB08C4"
    with oracle_connection() as conn:
        q = conn.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
        assert q.fetchone() == ("RABAEV", "orcl")
        q.execute("select NAME from RRL_WARES where ID=:w", w=f["warehouse_id"])
        assert q.fetchone() == ("TRADECASE QA c3ab08c4",)
    case.OUT = OUT;case.FILE = STATE
    case.s = json.loads(STATE.read_text()) if STATE.exists() else dict(
        warehouse_id=f["warehouse_id"], article=f["article"], pick=f["pick"], history=[])
    case.w = f["warehouse_id"];case.tag = "PROFILE21."+str(case.w)
    case.base = f"/api/tradecase/warehouses/{case.w}"
    if "putaway" not in case.s:
        receipt = next(x["response"] for x in proof["http"] if x["status"] == 201)
        case.step("putaway", f"/api/receiving/putaway/{receipt['task_id']}/complete", dict(
            scanned_pallet=f["pallet"], scanned_from_cell=f["receive"], scanned_to_cell=receipt["putaway_cell"]))
    if "mark_valid" not in case.s:
        with oracle_connection() as conn:
            q = conn.cursor();q.execute("select PHYSICAL_UNIT_KEY,VERSION_NO from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w order by PHYSICAL_UNIT_KEY", w=case.w)
            units = list(q);assert len(units) == 10
        case.step("mark_valid", case.base+"/stock/mark-confirmations", dict(
            operation_id=case.tag+".valid", skm_id="TC03.SKM", external_event_id=case.tag+".valid",
            expected_site_version=1, occurred_at=datetime.now(timezone.utc).isoformat(),
            items=[dict(physical_unit_key=k, expected_attribute_version=v, verdict="VALID") for k, v in units]))


def measured_step(key, path, body, *args, **kwargs):
    if key not in {"launched", "picked"} or key in case.s:
        return original_step(key, path, body, *args, **kwargs)
    before = snapshot();start = datetime.now(timezone.utc).isoformat()
    try:
        return original_step(key, path, body, *args, **kwargs)
    finally:
        data = dict(start_at=start, finish_at=datetime.now(timezone.utc).isoformat(),
                    warehouse_id=case.w, step=key, sql=differences(before, snapshot()),
                    limits="One local new wave; shared v$sql counters include concurrent sessions and nested statements. Do not sum as wall time.")
        (OUT/("profile-"+key+".json")).write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT/"AGENTS.md").read_text(encoding="utf-8"))[1])
    original_step = case.step
    try:
        configure();case.step = measured_step
        case.prepare();case.execute()
    except Exception as exc:
        case.s["profile_error"] = str(exc);raise
    finally:
        case.s["history"] += CALLS;case.save()
