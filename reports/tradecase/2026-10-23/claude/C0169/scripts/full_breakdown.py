"""C-0169 READ ONLY: the full /api/admin/warehouses SQL (WarehouseService, limit 500) and its parts, warm-timed on one connection:
base columns only, + CELL_COUNT, + PALLET_COUNT, + TOTAL_REMAIN. Tells which correlated subquery costs the time."""
import json, pathlib, statistics, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.services.warehouse_service import WarehouseService

BASE = "ID,NAME,PREFIX,nvl(FLAG_RAW_MATERIAL,0) F1,nvl(FLAG_PRODUCTION,0) F2,nvl(FLAG_PRODUCTION_BUFFER,0) F3,nvl(FLAG_FINISHED_GOODS,0) F4,nvl(MES_ENABLED,0) F5,DEFAULT_RECEIVE_CELL,DEFAULT_ISSUE_CELL,WARE_COMMENT,OVERFLOW_CELL_NAME,PARENT_WARE_ID,ORD2"
CELLS = "(select count(*) from RRL_CELLS c where c.WARE_ID=w.ID) CELL_COUNT"
PALLETS = "(select count(distinct r.UID_POLETA) from RRL_CELLS c join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID=w.ID) PALLET_COUNT"
REMAIN = "(select nvl(sum(r.REMAIN),0) from RRL_CELLS c join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID=w.ID) TOTAL_REMAIN"
VARIANTS = {"base": [BASE], "+cells": [BASE, CELLS], "+pallets": [BASE, PALLETS], "+remain": [BASE, REMAIN], "full": [BASE, CELLS, PALLETS, REMAIN]}
res = {}
with OracleGateway().transaction("C-0169 warehouse breakdown READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, cols in VARIANTS.items():
        sql = f"select * from (select {','.join(cols)} from RRL_WARES w order by nvl(ORD2,ID),ID) where rownum<=500"
        ms = []
        for _ in range(6):
            t = time.perf_counter(); cur.execute(sql); rows = cur.fetchall(); ms.append(round((time.perf_counter() - t) * 1000, 1))
        res[name] = {"first_ms": ms[0], "warm_median": statistics.median(ms[1:]), "warm_min": min(ms[1:]), "warm_max": max(ms[1:]), "n_warm": 5, "rows": len(rows)}
    cur.execute("select index_name,listagg(column_name,',') within group(order by column_position) from user_ind_columns where table_name in('RRL_CELLS','RRL_REMAINS') group by index_name")
    res["indexes"] = [list(r) for r in cur.fetchall()]
    cur.execute("rollback")
svc = []
for _ in range(6):
    t = time.perf_counter(); rows = WarehouseService().list_warehouses(limit=500); svc.append(round((time.perf_counter() - t) * 1000, 1))
res["service_list_warehouses"] = {"first_ms": svc[0], "warm_median": statistics.median(svc[1:]), "warm_min": min(svc[1:]), "warm_max": max(svc[1:]), "n_warm": 5, "rows": len(rows)}
pathlib.Path(__file__).resolve().parents[1].joinpath("full-breakdown.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
