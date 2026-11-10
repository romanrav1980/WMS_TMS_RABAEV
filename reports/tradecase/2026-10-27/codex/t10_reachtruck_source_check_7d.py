"""Read-only T10 check that the live timeline exposes registered reach trucks."""
from datetime import datetime, timezone
import base64, json, re, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
API = "http://127.0.0.1:8093"
WAREHOUSES = [51365792, 213059748, 220639789, 222385707]
WINDOW = ("2026-10-20T18:00:00+00:00", "2026-10-27T18:00:00+00:00")
PASSWORD = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
AUTH = {"Authorization": "Basic " + base64.b64encode(f"admin:{PASSWORD}".encode()).decode()}
report = {"kind": "READ_ONLY_LIVE_TIMELINE", "started": datetime.now(timezone.utc).isoformat(), "window": WINDOW, "warehouses": {}}

for warehouse in WAREHOUSES:
    q = urllib.parse.urlencode({"warehouse_id": warehouse, "start_at": WINDOW[0], "finish_at": WINDOW[1]})
    req = urllib.request.Request(f"{API}/api/resources/timeline?{q}", headers=AUTH)
    with urllib.request.urlopen(req, timeout=120) as response:
        body = json.loads(response.read())
        kinds = sorted({item["kind"] for item in body["resources"]})
        row = {"http": response.status, "resources": len(body["resources"]), "resource_kinds": kinds,
               "reachtruck_lanes": sum(item["kind"] in {"REACHTRUCK", "REACH_TRUCK"} for item in body["resources"]),
               "events": len(body["events"]), "unscheduled": len(body["unscheduled"]),
               "assignments": len(body["assignments"]), "sources": {s["source_id"]: s["status"] for s in body["sources"]}}
        assert row["http"] == 200 and row["reachtruck_lanes"] > 0, (warehouse, row)
        report["warehouses"][str(warehouse)] = row

report["finished"] = datetime.now(timezone.utc).isoformat()
OUT = Path(__file__).with_name("t10_reachtruck_source_check_7d.json")
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
