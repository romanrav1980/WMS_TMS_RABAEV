"""C-0169 READ ONLY: the warehouse/driver selector reads measured in C-0167. SQL straight on Oracle (same text as the API) and the live
HTTP routes, first and warm calls separately, rows and result equality. Usage: measure.py <label> [repeats]."""
import base64, json, pathlib, re, statistics, sys, time
from urllib.request import Request, urlopen
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

ROOT = pathlib.Path("C:/projects/TMS")
label, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 6
FULL = re.search(r'"""(\s*select \*\s*from \(\s*select ID,.*?rownum <= :limit)"""', (ROOT / "api/wms_api_server/app/services/warehouse_service.py").read_text(encoding="utf-8"), re.S)
from app.modules.master_data.infrastructure.warehouse_options import _OPTIONS
DRIVERS = """SELECT ID, TRIM(F || ' ' || I || ' ' || O) AS FULL_NAME, F, I, O, TEL, TRANSPORT_NUM, SOBSTVENNYY, DOVERENNOST_OT
  FROM RABAEV.RRL_TR_VODITEL WHERE (DELETED IS NULL OR DELETED = 0) ORDER BY F, I"""
pw = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
auth = "Basic " + base64.b64encode(("admin:" + pw).encode()).decode()


def timed(fn):
    out = []
    for _ in range(n):
        t = time.perf_counter(); value = fn(); out.append((round((time.perf_counter() - t) * 1000, 1), value))
    return out


def http(path):
    with urlopen(Request("http://127.0.0.1:8088" + path, headers={"Authorization": auth}), timeout=60) as r:
        return json.loads(r.read())


def summary(samples):
    ms = [s[0] for s in samples]
    return {"first_ms": ms[0], "warm_min": min(ms[1:]), "warm_median": statistics.median(ms[1:]), "warm_max": max(ms[1:]), "n_warm": len(ms) - 1}


res = {"label": label}
gw = OracleGateway()
with gw.transaction("C-0169 selector SQL READ ONLY") as cur:
    cur.execute("set transaction read only")
    def run(sql, binds):
        def go():
            cur.execute(sql, binds); return cur.fetchall()
        return go
    if FULL:
        full = timed(run(FULL.group(1), {"limit": 500}))
        res["sql_full_warehouses"] = {**summary(full), "rows": len(full[0][1])}
    opts = timed(run(_OPTIONS, {"pattern": None, "after": None, "fetch": 501}))
    res["sql_options_warehouses"] = {**summary(opts), "rows": len(opts[0][1])}
    drv = timed(run(DRIVERS, {}))
    res["sql_drivers"] = {**summary(drv), "rows": len(drv[0][1])}
    if FULL:
        res["same_id_name_set"] = sorted((r[0], r[1]) for r in full[0][1]) == sorted((r[0], r[1]) for r in opts[0][1])
    cur.execute("select count(*) from RRL_WARES"); res["wares"] = cur.fetchone()[0]
    cur.execute("select count(*) from RRL_CELLS"); res["cells"] = cur.fetchone()[0]
    cur.execute("select count(*) from RRL_REMAINS"); res["remains"] = cur.fetchone()[0]
    cur.execute("rollback")
h_full = timed(lambda: http("/api/admin/warehouses?limit=500")); res["http_full_warehouses"] = {**summary(h_full), "rows": len(h_full[0][1])}
def all_options():
    items, after = [], None
    while True:
        page = http("/api/master-data/warehouses/options?limit=100" + (f"&after={after}" if after else ""))
        items += page["items"]; after = page["next_after"]
        if not after: return items
h_opt = timed(all_options); res["http_options_all_pages"] = {**summary(h_opt), "rows": len(h_opt[0][1])}
h_drv = timed(lambda: http("/api/admin/transport/drivers")); res["http_drivers"] = {**summary(h_drv), "rows": len(h_drv[0][1])}
key = lambda r: (int(r.get("ID", r.get("id"))), str(r.get("NAME", r.get("name"))))
res["http_same_id_name_set"] = sorted(map(key, h_full[0][1])) == sorted(map(key, h_opt[0][1]))
res["http_full_results_stable"] = len({json.dumps(s[1], sort_keys=True, default=str) for s in h_full}) == 1
out = pathlib.Path(__file__).resolve().parents[1] / f"measure-{label}.json"
out.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1, ensure_ascii=False))
