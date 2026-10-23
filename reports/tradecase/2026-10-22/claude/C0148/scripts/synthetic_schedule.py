"""C-0148: SYNTHETIC input to the existing native calculator RRL_TT_ROUTE_SCHEDULE.calculate (READ ONLY transaction).

No real trip contains depot + fresh road legs + destination rules + windows (checked 22.10), so the program example
(windows 11:00/11:55/12:40, return) cannot be verified on real data. This only shows that the existing calculator — which
the trip screen uses through /delivery-windows — reacts to order and to a 15 vs 45 minute detour. Values are invented
test input, never presented as a trip.
"""
import json, os, sys, pathlib
sys.path.insert(0, "C:/projects/TMS/scripts"); from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb

D = "2026-11-02 "


def source(stops, legs, windows, detour=None):
    rules = [{"address": a, "unload_norm_min": 15, "window_strict": 1, "address_count": 1} for a in stops]
    members = [{"address": a, "st_number": "SYN." + a, "delivery_window_from": D + windows[a][0], "delivery_window_to": D + windows[a][1]} for a in stops]
    return {"operations": [{"code": "DRIVE", "plan_start": D + "10:15:00", "plan_end": D + "10:15:00"},
                           {"code": "DRIVE_BACK", "plan_start": D + "13:30:00", "plan_end": D + "14:30:00"}],
            "route_material": {"order_valid": True, "depot_address": "SYN.DEPOT", "policy_id": "SYNTHETIC", "stops": stops,
                               "legs": [{"from_address": f, "to_address": t, "duration_min": m, "duration_basis": "ROAD_PROFILE_ESTIMATE", "fresh": True} for f, t, m in legs]},
            "destination_rules": rules, "members": members, "store_window_profiles": []}


WINDOWS = {"BRANCH": ("11:00:00", "11:15:00"), "STORE": ("11:55:00", "12:10:00"), "SHOP2": ("12:40:00", "13:25:00"), "EXTRA": ("10:00:00", "18:00:00")}
BASE = source(["BRANCH", "STORE", "SHOP2"], [("SYN.DEPOT", "BRANCH", 45), ("BRANCH", "STORE", 40), ("STORE", "SHOP2", 30), ("SHOP2", "SYN.DEPOT", 60)], WINDOWS)
REORDER = source(["STORE", "BRANCH", "SHOP2"], [("SYN.DEPOT", "STORE", 50), ("STORE", "BRANCH", 40), ("BRANCH", "SHOP2", 60), ("SHOP2", "SYN.DEPOT", 60)], WINDOWS)


def detour(extra):
    # Extra stop between STORE and SHOP2; together with its service (15) it costs `extra` minutes before SHOP2's strict window.
    half = (30 + extra - 15) / 2  # base STORE->SHOP2 drive is 30; extra = added drive + 15 service
    return source(["BRANCH", "STORE", "EXTRA", "SHOP2"], [("SYN.DEPOT", "BRANCH", 45), ("BRANCH", "STORE", 40), ("STORE", "EXTRA", half),
                                                        ("EXTRA", "SHOP2", half), ("SHOP2", "SYN.DEPOT", 60)], WINDOWS)


def main():
    e = os.environ
    con = oracledb.connect(user=e["WMS_ORACLE_USER"], password=e["WMS_ORACLE_PASSWORD"], dsn=e.get("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl"))
    cur = con.cursor(); cur.execute("set transaction read only")
    out = {"kind": "SYNTHETIC_INPUT_EXISTING_NATIVE_CALCULATOR", "read_only": True}
    for name, src in [("base", BASE), ("reordered", REORDER), ("detour_15", detour(15)), ("detour_45", detour(45))]:
        wire = cur.var(oracledb.DB_TYPE_CLOB); wire.setvalue(0, json.dumps(src)); res = cur.var(oracledb.DB_TYPE_CLOB)
        cur.callproc("RRL_TT_ROUTE_SCHEDULE.calculate", [wire, "Europe/Moscow", res])
        r = json.loads(res.getvalue().read())
        out[name] = {"status": r["status"], "return_at": r["return_at"], "issues": [i["code"] for i in r["issues"]],
                     "stops": [{k: s[k] for k in ("address", "arrival_at", "service_start_at", "wait_min", "late_min", "issues")} for s in r["stops"]]}
        print(name, r["status"], [(s["address"], (s["arrival_at"] or "")[11:16], s["wait_min"], s["late_min"]) for s in r["stops"]], "return", (r["return_at"] or "")[11:16], out[name]["issues"])
    con.rollback(); con.close()
    pathlib.Path(__file__).parent.parent.joinpath("synthetic-schedule.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


main()
