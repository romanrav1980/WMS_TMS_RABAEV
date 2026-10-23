"""C-0169 READ ONLY, review: three SQL forms for every filter mode — previous (correlated), group-by over all warehouses, and a bounded
CTE (the same filtered/ordered/limited warehouse set first, cells/remains aggregated only for it). Rows compared in order; every
sample is kept (n=10 each, first and warm separate); the plan of each is read from V$SQL_PLAN when visible."""
import json, pathlib, statistics, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

COLS = """ID,NAME,PREFIX,nvl(FLAG_RAW_MATERIAL,0) FLAG_RAW_MATERIAL,nvl(FLAG_PRODUCTION,0) FLAG_PRODUCTION,nvl(FLAG_PRODUCTION_BUFFER,0) FLAG_PRODUCTION_BUFFER,
 nvl(FLAG_FINISHED_GOODS,0) FLAG_FINISHED_GOODS,nvl(MES_ENABLED,0) MES_ENABLED,DEFAULT_RECEIVE_CELL,DEFAULT_ISSUE_CELL,WARE_COMMENT,OVERFLOW_CELL_NAME,PARENT_WARE_ID,ORD2"""
FORMS = {
 "previous": """select * from (select {cols},
   (select count(*) from RRL_CELLS c where c.WARE_ID=w.ID) CELL_COUNT,
   (select count(distinct r.UID_POLETA) from RRL_CELLS c join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID=w.ID) PALLET_COUNT,
   (select nvl(sum(r.REMAIN),0) from RRL_CELLS c join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID=w.ID) TOTAL_REMAIN
   from RRL_WARES w {where} order by nvl(ORD2,ID),ID) where rownum<=:limit""",
 "group_all": """select * from (select {cols},nvl(cc.CELL_COUNT,0) CELL_COUNT,nvl(st.PALLET_COUNT,0) PALLET_COUNT,nvl(st.TOTAL_REMAIN,0) TOTAL_REMAIN
   from RRL_WARES w left join(select WARE_ID,count(*) CELL_COUNT from RRL_CELLS group by WARE_ID) cc on cc.WARE_ID=w.ID
   left join(select c.WARE_ID,count(distinct r.UID_POLETA) PALLET_COUNT,sum(r.REMAIN) TOTAL_REMAIN from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL group by c.WARE_ID) st on st.WARE_ID=w.ID
   {where} order by nvl(ORD2,ID),ID) where rownum<=:limit""",
 "bounded_cte": """with sel as(select * from(select {cols} from RRL_WARES w {where} order by nvl(ORD2,ID),ID) where rownum<=:limit),
   cc as(select c.WARE_ID,count(*) CELL_COUNT from RRL_CELLS c where c.WARE_ID in(select ID from sel) group by c.WARE_ID),
   st as(select c.WARE_ID,count(distinct r.UID_POLETA) PALLET_COUNT,sum(r.REMAIN) TOTAL_REMAIN from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL
         where c.WARE_ID in(select ID from sel) group by c.WARE_ID)
   select sel.*,nvl(cc.CELL_COUNT,0) CELL_COUNT,nvl(st.PALLET_COUNT,0) PALLET_COUNT,nvl(st.TOTAL_REMAIN,0) TOTAL_REMAIN
   from sel left join cc on cc.WARE_ID=sel.ID left join st on st.WARE_ID=sel.ID order by nvl(sel.ORD2,sel.ID),sel.ID"""}
CASES = {"all_500": ("", {"limit": 500}), "default_200": ("", {"limit": 200}), "limit_5": ("", {"limit": 5}),
         "role_finished": ("where nvl(FLAG_FINISHED_GOODS,0)=1", {"limit": 500}), "mes_1": ("where nvl(MES_ENABLED,0)=:mes_enabled", {"limit": 500, "mes_enabled": 1}),
         "mes_0": ("where nvl(MES_ENABLED,0)=:mes_enabled", {"limit": 500, "mes_enabled": 0})}
res = {"cases": {}, "plans": {}}
with OracleGateway().transaction("C-0169 bounded CTE READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select count(*),sum(case when REMAIN<0 then 1 else 0 end),sum(case when REMAIN is null then 1 else 0 end) from RRL_REMAINS")
    res["remains_rows_negative_null"] = list(cur.fetchone())
    for name, (where, binds) in CASES.items():
        out, rows_by = {}, {}
        for form, sql in FORMS.items():
            text = sql.format(cols=COLS, where=where) + f" /* C0169 {form} {name} */"
            ms = []
            for _ in range(10):
                t = time.perf_counter(); cur.execute(text, binds); rows = cur.fetchall(); ms.append(round((time.perf_counter() - t) * 1000, 1))
            rows_by[form] = rows
            out[form] = {"samples_ms": ms, "first_ms": ms[0], "warm_median": statistics.median(ms[1:]), "warm_min": min(ms[1:]), "warm_max": max(ms[1:]), "n_warm": 9, "rows": len(rows)}
        out["group_all_equal"] = rows_by["group_all"] == rows_by["previous"]
        out["bounded_equal"] = rows_by["bounded_cte"] == rows_by["previous"]
        res["cases"][name] = out
    try:
        for form in FORMS:
            cur.execute("select sql_id,child_number from v$sql where sql_text like :t and sql_text not like '%v$sql%' fetch first 1 rows only", t=f"%C0169 {form} mes_1%")
            row = cur.fetchone()
            cur.execute("select operation||' '||options||' '||nvl(object_name,'') from v$sql_plan where sql_id=:s and child_number=:c order by id", s=row[0], c=row[1])
            res["plans"][form] = [r[0] for r in cur.fetchall()]
    except Exception as exc:
        res["plans"] = {"unavailable": str(exc).split("\n")[0]}
    cur.execute("rollback")
res["all_equal"] = all(c["group_all_equal"] and c["bounded_equal"] for c in res["cases"].values())
pathlib.Path(__file__).resolve().parents[1].joinpath("bounded.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
for k, v in res["cases"].items():
    print(k, "eq", v["group_all_equal"], v["bounded_equal"], "rows", v["previous"]["rows"], "| prev", v["previous"]["warm_median"], "| group", v["group_all"]["warm_median"], "| cte", v["bounded_cte"]["warm_median"], v["bounded_cte"]["samples_ms"])
print("neg/null", res["remains_rows_negative_null"], "all_equal", res["all_equal"])
print(json.dumps(res["plans"], indent=1)[:2500])
