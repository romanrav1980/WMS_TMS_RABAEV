"""C-0149: live READ ONLY check that yard permissions exist in the access catalog and the yard objects are absent before apply."""
import json, sys, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
out = {}
with OracleGateway().transaction("C-0149 permission catalog READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select table_name from user_tables where table_name like 'RRL_ACCESS%' order by 1")
    out["access_tables"] = [r[0] for r in cur.fetchall()]
    found = {}
    for t in out["access_tables"]:
        cur.execute("select column_name from user_tab_columns where table_name=:t and data_type like '%CHAR%'", t=t)
        for (col,) in cur.fetchall():
            cur.execute(f"select count(*) from {t} where {col} in('tradecase_view','tradecase_yard_operate','tradecase_operate')")
            n = cur.fetchone()[0]
            if n:
                cur.execute(f"select distinct {col} from {t} where {col} like 'tradecase%' order by 1")
                found[f"{t}.{col}"] = [r[0] for r in cur.fetchall()]
    out["tradecase_permissions"] = found
    cur.execute("select object_name,object_type from user_objects where object_name like 'RRL_YARD%' order by 1")
    out["yard_objects"] = [list(r) for r in cur.fetchall()]
print(json.dumps(out, ensure_ascii=False, indent=1))
pathlib.Path(__file__).parent.parent.joinpath('permission-catalog-live.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
