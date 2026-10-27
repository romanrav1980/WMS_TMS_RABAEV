"""C-0178 T08: real Oracle through the current application code (ASGI in-process; 8088 is restarted only by root).
Read-only capacity and top-up previews on trip T1 of warehouse 226192056 (not a protected set): first with the floor check bypassed (the
pre-C0178 behaviour, for comparison only), then the real code. One save with a fresh operation_id must be refused before any write;
proposal and hold counts are compared before/after. Nothing is created, so there is nothing to clean up."""
from datetime import datetime
import json
from pathlib import Path
import re
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from fastapi.testclient import TestClient
from app.main import app
from app.modules.integrations.infrastructure import trade_capacity, trade_topup
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-27/C0178"
PASSWORD = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
WARE, TRIP, SKU, NEED = 226192056, "T1", "A", "N1"
BASE = f"/api/tradecase/warehouses/{WARE}/trips/{TRIP}"
client = TestClient(app, raise_server_exceptions=False)
report = dict(status="FAIL", mode="ASGI in-process current code + real Oracle", warehouse=WARE, trip=TRIP, started=datetime.now().isoformat(), calls=[])


def call(method, path, body=None, auth=("admin", PASSWORD)):
    start = time.perf_counter()
    r = client.request(method, path, json=body, auth=auth)
    value = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:300]
    report["calls"].append(dict(method=method, path=path, status=r.status_code, ms=round((time.perf_counter() - start) * 1000, 1)))
    return dict(status=r.status_code, body=value)


def counts():
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only")
        q.execute("""select (select count(*) from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=:w),(select count(*) from RRL_TRADE_TOPUP_HOLD h join RRL_TRADE_TOPUP_PROPOSAL p
            on p.PROPOSAL_ID=h.PROPOSAL_ID where p.WARE_ID=:w),(select count(*) from RRL_TRADE_TOPUP_HOLD h join RRL_TRADE_TOPUP_PROPOSAL p
            on p.PROPOSAL_ID=h.PROPOSAL_ID where p.WARE_ID=:w and h.STATUS='ACTIVE') from dual""", w=WARE)
        return dict(zip(("proposals", "holds", "active_holds"), q.fetchone()))


def previews():
    return dict(capacity_1=call("GET", f"{BASE}/capacity?sku_id={SKU}&requested_boxes=1"),
                capacity_100000=call("GET", f"{BASE}/capacity?sku_id={SKU}&requested_boxes=100000"),
                topup=call("POST", f"{BASE}/topup-preview", dict(need_ids=[NEED], max_age_minutes=1440)))


def run():
    report["before_counts"] = counts()
    real = trade_capacity.floor_admission
    bypass = lambda cur, vehicle: dict(real(cur, vehicle), blocking_reason=None)  # comparison only: what the code did before C0178
    trade_capacity.floor_admission = trade_topup.floor_admission = bypass
    report["bypassed"] = previews()
    trade_capacity.floor_admission = trade_topup.floor_admission = real
    report["real"] = previews()
    report["save"] = call("POST", f"{BASE}/topup-proposals", dict(operation_id="C0178.SAVE." + uuid4().hex[:10], need_ids=[NEED], max_age_minutes=1440))
    report["other_warehouse"] = call("GET", f"/api/tradecase/warehouses/999999001/trips/{TRIP}/capacity?sku_id={SKU}&requested_boxes=1")
    report["wrong_password"] = call("GET", f"{BASE}/capacity?sku_id={SKU}&requested_boxes=1", auth=("admin", "wrong-" + uuid4().hex[:6]))
    report["after_counts"] = counts()
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only")
        q.execute("""select * from (select ELAPSED_MS,API_PATH,substr(SQL_TEXT,1,120) from RRL_SQL_SLOW_LOG where CREATED_AT>=to_timestamp(:t,'YYYY-MM-DD"T"HH24:MI:SS.FF')
            order by ELAPSED_MS desc) where rownum<=3""", t=report["started"])
        report["slow_log"] = [list(r) for r in q.fetchall()]
    real_reasons = [report["real"]["capacity_1"]["body"].get("blocking_reason"), report["real"]["capacity_100000"]["body"].get("blocking_reason")]
    assert real_reasons == ["TOPUP_PALLET_PLACE_MAPPING_REQUIRED"] * 2, real_reasons
    assert report["before_counts"] == report["after_counts"]
    report["status"] = "RUN_COMPLETE"


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        report["error"] = repr(exc)[:1500]; raise
    finally:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "floor-capacity-live.json").write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        print(json.dumps({k: report.get(k) for k in ("status", "error", "before_counts", "after_counts", "slow_log")}, default=str))
