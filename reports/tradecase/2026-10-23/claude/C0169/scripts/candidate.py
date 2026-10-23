"""C-0169 READ ONLY candidate: the same columns, order and limit, with cells and remains aggregated once per warehouse (group by)
instead of three correlated subqueries per warehouse. Compares the full result row by row with the current SQL and times both."""
import json, pathlib, statistics, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

COLS = """w.ID,w.NAME,w.PREFIX,nvl(w.FLAG_RAW_MATERIAL,0) FLAG_RAW_MATERIAL,nvl(w.FLAG_PRODUCTION,0) FLAG_PRODUCTION,
 nvl(w.FLAG_PRODUCTION_BUFFER,0) FLAG_PRODUCTION_BUFFER,nvl(w.FLAG_FINISHED_GOODS,0) FLAG_FINISHED_GOODS,nvl(w.MES_ENABLED,0) MES_ENABLED,
 w.DEFAULT_RECEIVE_CELL,w.DEFAULT_ISSUE_CELL,w.WARE_COMMENT,w.OVERFLOW_CELL_NAME,w.PARENT_WARE_ID,w.ORD2"""
CURRENT = f"""select * from (select {COLS},
 (select count(*) from RRL_CELLS c where c.WARE_ID=w.ID) CELL_COUNT,
 (select count(distinct r.UID_POLETA) from RRL_CELLS c join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID=w.ID) PALLET_COUNT,
 (select nvl(sum(r.REMAIN),0) from RRL_CELLS c join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID=w.ID) TOTAL_REMAIN
 from RRL_WARES w {{where}} order by nvl(w.ORD2,w.ID),w.ID) where rownum<=:limit"""
CANDIDATE = f"""select * from (select {COLS},
 nvl(cc.CELL_COUNT,0) CELL_COUNT,nvl(st.PALLET_COUNT,0) PALLET_COUNT,nvl(st.TOTAL_REMAIN,0) TOTAL_REMAIN
 from RRL_WARES w
 left join(select WARE_ID,count(*) CELL_COUNT from RRL_CELLS group by WARE_ID) cc on cc.WARE_ID=w.ID
 left join(select c.WARE_ID,count(distinct r.UID_POLETA) PALLET_COUNT,sum(r.REMAIN) TOTAL_REMAIN
   from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL group by c.WARE_ID) st on st.WARE_ID=w.ID
 {{where}} order by nvl(w.ORD2,w.ID),w.ID) where rownum<=:limit"""
CASES = {"all_500": ("", {"limit": 500}), "limit_200": ("", {"limit": 200}), "limit_5": ("", {"limit": 5}),
         "role_finished": ("where nvl(w.FLAG_FINISHED_GOODS,0)=1", {"limit": 500}), "mes_1": ("where nvl(w.MES_ENABLED,0)=:mes_enabled", {"limit": 500, "mes_enabled": 1})}
res = {"cases": {}}
with OracleGateway().transaction("C-0169 candidate READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, (where, binds) in CASES.items():
        out = {}
        for kind, sql in (("current", CURRENT), ("candidate", CANDIDATE)):
            ms = []
            for _ in range(6):
                t = time.perf_counter(); cur.execute(sql.format(where=where), binds); rows = cur.fetchall(); ms.append(round((time.perf_counter() - t) * 1000, 1))
            out[kind] = {"first_ms": ms[0], "warm_median": statistics.median(ms[1:]), "warm_min": min(ms[1:]), "warm_max": max(ms[1:]), "n_warm": 5, "rows": len(rows), "_rows": rows}
        out["equal_rows_in_order"] = out["current"].pop("_rows") == out["candidate"].pop("_rows")
        res["cases"][name] = out
    cur.execute("rollback")
res["all_equal"] = all(c["equal_rows_in_order"] for c in res["cases"].values())
pathlib.Path(__file__).resolve().parents[1].joinpath("candidate.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
for k, v in res["cases"].items(): print(k, "equal", v["equal_rows_in_order"], "rows", v["current"]["rows"], "current", v["current"]["warm_median"], "candidate", v["candidate"]["warm_median"], "first", v["current"]["first_ms"], v["candidate"]["first_ms"])
print("all_equal", res["all_equal"])
