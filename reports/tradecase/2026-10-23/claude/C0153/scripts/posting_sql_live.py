"""C-0153: READ ONLY: index for the hold check and timing of the write-off describe queries on real pallets (no writes)."""
import json, sys, time, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
out = {}
with OracleGateway().transaction("C-0153 posting SQL READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select index_name,listagg(column_name,',')within group(order by column_position) from user_ind_columns where table_name='RRL_QUALITY_HOLD' group by index_name")
    out["hold_indexes"] = cur.fetchall(); print(out["hold_indexes"])
    cur.execute("""select u.CURRENT_UID,count(*) n from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
      where u.STOCK_STATUS<>'ISSUED' group by u.CURRENT_UID order by n desc fetch first 1 rows only""")
    uid, n = cur.fetchone(); out["largest_trade_pallet_units"] = n
    q = {"hold_check": ("select count(*) from RRL_QUALITY_HOLD where ENTITY_TYPE='PALLET' and ENTITY_ID=:u and HOLD_STATUS='ACTIVE'", {"u": uid}),
         "units_wire": ("""select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key' value u.PHYSICAL_UNIT_KEY,'version' value u.UNIT_VERSION) returning clob)
            from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=:u and u.STOCK_STATUS<>'ISSUED'""", {"u": uid}),
         "codes_profiles": ("""select count(distinct c.SYSTEM_CODE) from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
            where u.CURRENT_UID=:u and u.STOCK_STATUS<>'ISSUED'""", {"u": uid}),
         "composition_text": ("""select count(*) from RRL_WMS_RECEIPT_UNIT u left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
            where u.CURRENT_UID=:u and u.STOCK_STATUS<>'ISSUED'""", {"u": uid})}
    for name, (sql, params) in q.items():
        ms = []
        for _ in range(3):
            t = time.perf_counter(); cur.execute(sql, params); cur.fetchall(); ms.append(round((time.perf_counter() - t) * 1000, 1))
        out[name] = ms; print(name, ms)
pathlib.Path(__file__).parent.parent.joinpath("posting-sql-live.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
