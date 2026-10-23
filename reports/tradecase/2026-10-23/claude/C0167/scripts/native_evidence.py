"""C-0167 LIVE READ ONLY: the current native rules of vehicle change, loading, unloading, departure and the trade manifest, read from
USER_SOURCE / USER_TRIGGERS with SHA-256. Proves which transitions already exist; nothing is executed or written."""
import hashlib, json, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

CHECKS = {
    ("RRL_TRANSPORT_EDIT_API", "PACKAGE BODY"): {
        "loaded_or_departed_refused": "STATUS in('LOADED','DEPARTED');\n   if v_count>0 then raise_application_error(-20886,'TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT')",
        "capacity_check_of_new_vehicle": "RRL_TRANSPORT_PLAN_RULES.check_vehicle(new_vehicle,sts.to_clob,0,v_check)",
        "concurrent_vehicle_change": "TRANSPORT_VEHICLE_CHANGED_RETRY",
        "frozen_after_shipping": "TRANSPORT_PLAN_FROZEN",
        "assignments_untouched": "update RRL_TRANSPORT_TASK set TRANSPORT=requested.TRANSPORT"},
    ("RRL_STOCK_HU_LOAD_CORE", "PACKAGE BODY"): {
        "scan_must_be_current_vehicle": "ctx.get_string('scan_vehicle')!=tt.TRANSPORT",
        "execute_closure_on_vehicle": "tt.TRANSPORT!=j.get_string('vehicle')",
        "vehicle_capacity": "LOAD_ACTIVE_VEHICLE_CAPACITY_REQUIRE"},
    ("RRL_STOCK_TRIP_DEPART_CMD", "PACKAGE BODY"): {"loads_on_current_vehicle": "lf.VEHICLE_ID=vehicle_no and lf.VEHICLE_NUMBER=tt.TRANSPORT"},
    ("RRL_STOCK_UNLOAD_CMD", "PACKAGE BODY"): {
        "unload_scan_vehicle_dock_cell_reason": "UNLOAD_ORIGINAL_PLACE_VEHICLE_DOCK_CELL_SCAN_REQUIRED",
        "unload_only_on_current_undeparted_vehicle": "trip.TRANSPORT!=p_lf.VEHICLE_NUMBER"},
    ("RRL_TRADE_TRANSPORT_CORE", "PACKAGE BODY"): {
        "manifest_contains_vehicle": "d.put('vehicle',plate)",
        "departure_needs_document_of_current_manifest": "d.MANIFEST_SIGNATURE<>signature(p_trip)"},
}
res = {"objects": {}, "trigger": {}}
with OracleGateway().transaction("C-0167 native evidence READ ONLY") as cur:
    cur.execute("set transaction read only")
    for (name, kind), checks in CHECKS.items():
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        text = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
        res["objects"][f"{name}:{kind}"] = {"sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
                                            "checks": {k: v in text for k, v in checks.items()}}
    cur.execute("select TRIGGER_BODY,TRIGGERING_EVENT,STATUS from USER_TRIGGERS where TRIGGER_NAME='RRL_TT_PHYSICAL_DEPART_GUARD'")
    body, event, status = cur.fetchone()
    body = body.replace("\r", "")
    res["trigger"] = {"name": "RRL_TT_PHYSICAL_DEPART_GUARD", "event": event, "status": status,
                      "sha256": hashlib.sha256(body.encode()).hexdigest().upper(),
                      "refuses_vehicle_change_when_loaded": "nvl(:new.TRANSPORT,chr(0))!=nvl(:old.TRANSPORT,chr(0))" in body
                          and "TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT" in body}
    cur.execute("rollback")
res["all_true"] = all(all(o["checks"].values()) for o in res["objects"].values()) and res["trigger"]["refuses_vehicle_change_when_loaded"]
pathlib.Path(__file__).resolve().parents[1].joinpath("native-evidence.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
