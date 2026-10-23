"""C-0158: the real resource timeline read (this checkout's code, live DB, READ ONLY) for a TRADECASE site. Before the dock-plan kit is
applied the plan read fails as 'object missing' and is skipped: the yard source must stay READY with its visit events, and no plan
event may appear. Also times the read."""
import json, pathlib, sys, time
from datetime import datetime, timedelta, timezone
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.resources.public import build_resource_timeline

out = {}
for ware in (220793322, 210564699):
    finish = datetime.now(timezone.utc).replace(microsecond=0); start = finish - timedelta(days=1)
    t = time.perf_counter()
    try:
        r = build_resource_timeline(OracleGateway()).read(ware, start, finish, "admin")
        yard = next((s for s in r["sources"] if s["source_id"] == "yard"), None)
        out[ware] = {"ms": round((time.perf_counter() - t) * 1000, 1), "yard_source": yard and yard["status"],
                     "yard_events": sum(1 for e in r["events"] if e["kind"].startswith("YARD_")), "plan_events": sum(1 for e in r["events"] if e["kind"] == "YARD_DOCK_PLAN"),
                     "events": len(r["events"])}
    except Exception as e:  # noqa: BLE001 - recorded, not hidden
        out[ware] = {"error": repr(e)[:300]}
    print(ware, out[ware])
pathlib.Path(__file__).parent.parent.joinpath("timeline-live.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
