"""C-0169 READ ONLY after-check: the changed WarehouseService.list_warehouses (new SQL, real gateway) against the previous SQL text for
every filter mode; rows equal in order, plus warm timing of the service call itself."""
import json, pathlib, statistics, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server'); sys.path.insert(0, str(pathlib.Path(__file__).parent))
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.services.warehouse_service import WarehouseService
from candidate import CURRENT

CASES = {"all_500": (dict(limit=500), "", {"limit": 500}), "default_200": (dict(), "", {"limit": 200}), "limit_5": (dict(limit=5), "", {"limit": 5}),
         "role_finished": (dict(role="FINISHED_GOODS", limit=500), "where nvl(w.FLAG_FINISHED_GOODS,0)=1", {"limit": 500}),
         "mes_1": (dict(mes_enabled=1, limit=500), "where nvl(w.MES_ENABLED,0)=:mes_enabled", {"limit": 500, "mes_enabled": 1}),
         "mes_0": (dict(mes_enabled=0, limit=500), "where nvl(w.MES_ENABLED,0)=:mes_enabled", {"limit": 500, "mes_enabled": 0})}
res = {"cases": {}}
gw = OracleGateway()
for name, (kwargs, where, binds) in CASES.items():
    with gw.transaction("C-0169 previous SQL READ ONLY") as cur:
        cur.execute("set transaction read only"); cur.execute(CURRENT.format(where=where), binds)
        cols = [d[0].lower() for d in cur.description]; before = [dict(zip(cols, r)) for r in cur.fetchall()]; cur.execute("rollback")
    ms = []
    for _ in range(6):
        t = time.perf_counter(); after = WarehouseService().list_warehouses(**kwargs); ms.append(round((time.perf_counter() - t) * 1000, 1))
    norm = lambda rows: [{k.lower(): v for k, v in r.items()} for r in rows]
    res["cases"][name] = {"rows": len(after), "equal_in_order": norm(after) == norm(before), "first_ms": ms[0], "warm_median": statistics.median(ms[1:]),
                          "warm_min": min(ms[1:]), "warm_max": max(ms[1:]), "n_warm": 5}
res["all_equal"] = all(c["equal_in_order"] for c in res["cases"].values())
pathlib.Path(__file__).resolve().parents[1].joinpath("after.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
for k, v in res["cases"].items(): print(k, v)
print("all_equal", res["all_equal"])
