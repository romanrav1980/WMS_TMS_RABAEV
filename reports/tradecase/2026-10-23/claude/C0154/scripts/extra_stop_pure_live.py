"""C-0154: the PURE part of RRL_TRADE_EXTRA_STOP_API (exact text from the migration) executed as an anonymous PL/SQL block in a READ ONLY
transaction against the real native RRL_TT_ROUTE_SCHEDULE.calculate. Input = the program's own example (section 10 matrix/windows,
section 12 extra stop 15/45 min). SYNTHETIC route data, real calculator; nothing is installed or written."""
import json, sys, pathlib
sys.path.insert(0, "C:/projects/TMS/scripts"); sys.path.insert(0, "C:/projects/TMS/api/wms_api_server")
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway

SQL = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_extra_stop/002_api.sql").read_text(encoding="utf-8")
PURE = SQL[SQL.index(" -- PURE BEGIN"):SQL.index(" -- PURE END")]
BLOCK = "declare\n" + PURE + "\nbegin\n :out := evaluate_source(:src, :req, :legs);\nend;"
D = "2026-11-02 "
# Program section 10: travel minutes, row = from, column = to. Section 12 scenario: store window end 13:40 and resource end 14:40 make the
# binding slack exactly 30 minutes under the native times (which include the mandatory 15-minute rest after 120 minutes of driving).
M = {("DEPOT", "HUB"): 60, ("DEPOT", "BRANCH"): 75, ("DEPOT", "STORE"): 90, ("HUB", "DEPOT"): 60, ("HUB", "BRANCH"): 40, ("HUB", "STORE"): 70,
     ("BRANCH", "DEPOT"): 75, ("BRANCH", "HUB"): 40, ("BRANCH", "STORE"): 30, ("STORE", "DEPOT"): 60, ("STORE", "HUB"): 70, ("STORE", "BRANCH"): 30}
ROUTE = ["HUB", "BRANCH", "STORE"]


def source(store_close="14:00:00", envelope="14:30:00"):
    windows = {"HUB": ("11:00:00", "12:00:00"), "BRANCH": ("11:30:00", "13:00:00"), "STORE": ("12:00:00", store_close)}
    pairs = list(zip(["DEPOT", *ROUTE], [*ROUTE, "DEPOT"]))
    return {"operations": [{"code": "DRIVE", "plan_start": D + "10:00:00", "plan_end": D + "10:00:00"},
                           {"code": "DRIVE_BACK", "plan_start": D + "13:00:00", "plan_end": D + envelope}],
            "route_material": {"order_valid": True, "depot_address": "DEPOT", "policy_id": "SYNTHETIC_PROGRAM_EXAMPLE", "stops": ROUTE,
                               "legs": [{"from_address": a, "to_address": b, "duration_min": M[(a, b)], "duration_basis": "ROAD_PROFILE_ESTIMATE", "fresh": True} for a, b in pairs]},
            "destination_rules": [{"address": a, "unload_norm_min": 15, "window_strict": 1, "address_count": 1} for a in ROUTE],
            "members": [{"address": a, "st_number": "SYN." + a, "route_ordinal": (i + 1) * 10, "delivery_window_from": D + windows[a][0],
                         "delivery_window_to": D + windows[a][1]} for i, a in enumerate(ROUTE)],
            "store_window_profiles": []}


def legs(extra):
    # Every insertion position costs `extra` minutes including the 15-minute service: A->X + X->B = A->B + (extra - 15).
    out = [{"from_address": a, "to_address": b, "duration_min": m} for (a, b), m in M.items()]
    for a, b in zip(["DEPOT", *ROUTE], [*ROUTE, "DEPOT"]):
        half = (M[(a, b)] + extra - 15) / 2
        out += [{"from_address": a, "to_address": "EXTRA", "duration_min": half}, {"from_address": "EXTRA", "to_address": b, "duration_min": half}]
    return out


RULE = {"address_count": 1, "unload_norm_min": 15, "window_strict": 0, "synthetic_window_from": D + "09:00:00", "synthetic_window_to": D + "18:00:00"}
CASES = {
    "base_section10": (source(envelope="16:00:00"), {"address": "HUB", "zone": "Europe/Moscow", "extra_rule": RULE}, None),
    "extra_15_slack_30": (source("13:40:00", "14:40:00"), {"address": "EXTRA", "zone": "Europe/Moscow", "extra_rule": RULE}, legs(15)),
    "extra_45_slack_30": (source("13:40:00", "14:40:00"), {"address": "EXTRA", "zone": "Europe/Moscow", "extra_rule": RULE}, legs(45)),
    "new_stops_forbidden": (source("13:40:00", "14:40:00"), {"address": "EXTRA", "zone": "Europe/Moscow", "extra_rule": RULE, "new_stops_forbidden": True}, legs(15)),
    "extra_legs_unknown": (source("13:40:00", "14:40:00"), {"address": "EXTRA", "zone": "Europe/Moscow", "extra_rule": RULE}, [l for l in legs(15) if l["to_address"] != "EXTRA"]),
    "extra_rule_missing": (source("13:40:00", "14:40:00"), {"address": "EXTRA", "zone": "Europe/Moscow", "extra_rule": {**RULE, "unload_norm_min": None}}, legs(15)),
}


def main():
    out = {"kind": "SYNTHETIC_PROGRAM_EXAMPLE_REAL_NATIVE_CALCULATOR_READ_ONLY", "package_text": "PURE section of 002_api.sql, executed unchanged"}
    with OracleGateway().transaction("C-0154 extra stop pure READ ONLY") as cur:
        cur.execute("set transaction read only")
        for name, (src, req, lg) in CASES.items():
            res = cur.var(oracledb.DB_TYPE_CLOB)
            s, q, l = cur.var(oracledb.DB_TYPE_CLOB), cur.var(oracledb.DB_TYPE_CLOB), cur.var(oracledb.DB_TYPE_CLOB)
            s.setvalue(0, json.dumps(src)); q.setvalue(0, json.dumps(req)); l.setvalue(0, json.dumps(lg) if lg is not None else None)
            cur.execute(BLOCK, out=res, src=s, req=q, legs=l)
            r = json.loads(res.getvalue().read())
            out[name] = r
            hm = lambda x: (x or "")[11:16]
            stops = [(x["address"], hm(x["arrival_at"]), hm(x.get("service_finish_at"))) for x in (r.get("after") or r.get("before") or {}).get("stops", [])]
            print(f"{name}: {r['decision']} {r.get('reason', '')} pos={r.get('position')} slack {r.get('before_slack_min')}->{r.get('after_slack_min')}"
                  f" added={r.get('added_min')} stops={stops} return={hm((r.get('after') or r.get('before') or {}).get('return_at'))}")
    pathlib.Path(__file__).parent.parent.joinpath("extra-stop-pure-live.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


main()
