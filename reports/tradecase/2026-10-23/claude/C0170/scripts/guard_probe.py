"""C-0170 LIVE READ ONLY: call the current RRL_TRADE_STOCK_GUARD.assert_command_stock (public, read-only checks that raise) on one
existing trade pallet with stock, for the short commands versus commands it already knows. No posting, no write (read-only tx)."""
import json, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway

res = {"probes": []}
with OracleGateway().transaction("C-0170 guard probe READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("""select r.UID_POLETA,c.WARE_ID,r.REMAIN from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL
        where r.REMAIN>0 and c.WARE_ID<>225837931 and exists(select 1 from RRL_TRADE_SITE s where s.WARE_ID=c.WARE_ID)
          and exists(select 1 from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=r.UID_POLETA)
          and not exists(select 1 from RRL_QUALITY_HOLD h where h.ENTITY_TYPE='PALLET' and h.ENTITY_ID=r.UID_POLETA and h.HOLD_STATUS='ACTIVE')
        order by c.WARE_ID desc fetch first 1 rows only""")
    uid, ware, remain = cur.fetchone(); res["pallet"] = {"uid": uid, "warehouse_id": ware, "remain": float(remain)}
    for kind, source, metadata in (("CASE_SHORT_APPROVE", {"short_id": 1}, {"decision": "RESTORE"}),
                                   ("CASE_SHORT_APPROVE", {"short_id": 1}, {"decision": "ACCEPT_SHORT"}),
                                   ("CASE_SHORT_APPROVE", {"short_id": 1}, {"decision": "READY"}),
                                   ("INVENTORY_COUNT", {"revision_id": 1}, {}),
                                   ("WAVE_RESERVE_SOURCES", {}, {})):
        req = json.dumps({"operation_id": "C0170.PROBE", "command_type": kind, "source": source, "metadata": metadata})
        try:
            cur.callproc("RRL_TRADE_STOCK_GUARD.assert_command_stock", [uid, req, "admin"]); outcome = "ALLOWED"
        except oracledb.DatabaseError as exc:
            outcome = str(exc.args[0]).split("\n")[0]
        res["probes"].append({"command_type": kind, "decision": metadata.get("decision"), "outcome": outcome})
    cur.execute("rollback")
pathlib.Path(__file__).resolve().parents[1].joinpath("guard-probe.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
