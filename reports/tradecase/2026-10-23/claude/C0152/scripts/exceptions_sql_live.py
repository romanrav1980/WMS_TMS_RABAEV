"""C-0152: READ ONLY timing of the SQL the exceptions read uses (package not applied: equivalent statements, no writes)."""
import json, sys, time, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
VIS = """(select count(*) from RRL_WMS_RECEIPT_UNIT u left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
  where u.CURRENT_UID=r.UID_POLETA and u.STOCK_STATUS<>'ISSUED' and (a.OWNER_ID is null or RRL_TRADE_STOCK_GUARD.owner_allowed(:actor,:ware,a.OWNER_ID,0)<>1))"""
Q = {
 "quarantine": f"""select count(*) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
   where c.WARE_ID=:ware and nvl(c.BLOCKED_FOR_REMAINS,0)=1 and r.REMAIN>0 and {VIS}=0""",
 "discrepancies": """select count(*) from RRL_INVENTORY_TASK t where t.WARE_ID=:ware and(t.STATUS not in('DONE','CANCELLED','CLOSED')
   or(t.FACT_QTY is not null and t.FACT_QTY<>nvl(t.PLANNED_QTY,-1))) and not exists(select 1 from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a
   on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_CELL=t.CELL_CODE and u.STOCK_STATUS<>'ISSUED'
   and RRL_TRADE_STOCK_GUARD.owner_allowed(:actor,:ware,a.OWNER_ID,0)<>1)""",
 "composition_of_largest_pallet": """select max(n) from(select count(*) n from RRL_WMS_RECEIPT_UNIT u join RRL_CELLS c on c.CELL=u.CURRENT_CELL
   where c.WARE_ID=:ware and u.STOCK_STATUS<>'ISSUED' group by u.CURRENT_UID)""",
}
out = {}
for ware in (220793322, 215590763):
    with OracleGateway().transaction("C-0152 exceptions SQL READ ONLY") as cur:
        cur.execute("set transaction read only")
        for name, sql in Q.items():
            ms = []
            for _ in range(3):
                t = time.perf_counter(); params = {"ware": ware} | ({"actor": "admin"} if ":actor" in sql else {})
                cur.execute(sql, params); value = cur.fetchone()[0]; ms.append(round((time.perf_counter() - t) * 1000, 1))
            out[f"{ware}/{name}"] = {"rows": value, "ms": ms}; print(ware, name, value, ms)
pathlib.Path(__file__).parent.parent.joinpath("exceptions-sql-live.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
