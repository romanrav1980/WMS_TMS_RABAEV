"""C-0164 LIVE READ ONLY: the candidate compose() runs unchanged in an anonymous block (set transaction read only) on real assembled
trade orders (CASE and full pallet fulfillments); its signature and closure are recomputed in Python from the fulfillment rows. No package is created, nothing is written."""
import hashlib, json, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway

body = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_composition_ack/002_composition_api.sql").read_text(encoding="utf-8").replace("\r\n", "\n")
body = body[body.index("create or replace package body"):]
helpers = body[body.index(" procedure fail("):body.index(" -- Same order as the document intake")]
compose = body[body.index(" procedure compose("):body.index(" -- Stored snapshot + live reconciliation")]
block = "declare\n sig varchar2(64);units number;carriers number;codes number;closed number;items json_array_t;\n" + helpers + compose + """
begin
 compose(:o,true,sig,units,carriers,codes,closed,items);
 :sig:=sig;:units:=units;:carriers:=carriers;:codes:=codes;:closed:=closed;:items:=items.to_clob;
end;"""
NL = chr(10)
OUT = pathlib.Path(__file__).resolve().parents[1]
res = {"orders": []}
with OracleGateway().transaction("C-0164 candidate compose READ ONLY") as cur:
    cur.execute("set transaction read only")
    # Real trade orders with picked/shipped fulfillments, at least one of them a full pallet (warehouse task), when present.
    cur.execute("""select * from(select l.CUSTOMER_ORDER_ID,l.EXTERNAL_ID,l.WARE_ID,max(case when f.PICKED_WAREHOUSE_TASK_ID is not null then 1 else 0 end)FP
      from RRL_TRADE_ORDER_LINK l join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.CUSTOMER_ORDER_ID=l.CUSTOMER_ORDER_ID where f.STATUS in('PICKED','SHIPPED')
      group by l.CUSTOMER_ORDER_ID,l.EXTERNAL_ID,l.WARE_ID order by FP desc,1 desc)fetch first 5 rows only""")
    picked = cur.fetchall()
    # And one trade order whose assembly is still open (a PLANNED fulfillment): it must not count as assembled.
    cur.execute("""select l.CUSTOMER_ORDER_ID,l.EXTERNAL_ID,l.WARE_ID,0 from RRL_TRADE_ORDER_LINK l where exists(select 1 from RRL_CUSTOMER_ORDER_FULFILLMENT f
      where f.CUSTOMER_ORDER_ID=l.CUSTOMER_ORDER_ID and f.STATUS='PLANNED') order by 1 desc fetch first 1 rows only""")
    for order, ext, ware, fp in picked + cur.fetchall():
        v = {k: cur.var(oracledb.DB_TYPE_VARCHAR if k == "sig" else oracledb.DB_TYPE_CLOB if k == "items" else oracledb.DB_TYPE_NUMBER) for k in ("sig", "units", "carriers", "codes", "closed", "items")}
        cur.execute(block, o=order, **v)
        got = {k: (x.getvalue().read() if k == "items" and x.getvalue() else x.getvalue()) for k, x in v.items()}
        # Independent Python recomputation of the signature rule from the fulfillment rows.
        cur.execute("""select FULFILLMENT_ID,nvl(PICKED_PALLET_UID,PALLET_UID),STATUS,PICKED_CASE_TASK_ID,PICKED_CONTENT_VERSION,PICKED_WAREHOUSE_TASK_ID,
          PICKED_STOCK_VERSION,RRL_STOCK_PLAN_HELPER.decimal_text(FACT_QTY),FACT_UOM,FACT_COMPOSITION_JSON from RRL_CUSTOMER_ORDER_FULFILLMENT
          where CUSTOMER_ORDER_ID=:o order by FULFILLMENT_ID""", o=order)
        lines, open_rows, total = [], 0, 0
        for fid, carrier, status, case_id, cver, wh_id, sver, qty, uom, fact in cur.fetchall():
            total += 1
            if status not in ("PICKED", "SHIPPED") or (case_id is None and wh_id is None):
                open_rows += 1; continue
            text = fact.read() if fact is not None else None
            fh = hashlib.sha256(text.encode()).hexdigest() if text is not None else "-"
            lines.append("|".join(["F", str(fid), carrier or "", "" if case_id is None else str(case_id), "" if cver is None else str(cver),
                                   "" if wh_id is None else str(wh_id), "" if sver is None else str(sver), qty or "", uom or "", fh]))
        python_sig = hashlib.sha256(NL.join(lines).encode()).hexdigest() if lines else None
        items = json.loads(got["items"]) if got["items"] else []
        ful = [i for i in items if i["kind"] == "FULFILLMENT"]; un = [i for i in items if i["kind"] == "UNIT"]
        res["orders"].append({"warehouse_id": ware, "order_id": ext, "has_full_pallet": fp == 1, "native_signature": got["sig"], "python_signature": python_sig,
                              "signature_equal": got["sig"] == python_sig, "carriers": got["carriers"], "units": got["units"], "codes": got["codes"],
                              "assembly_closed": got["closed"] == 1, "python_closed": total > 0 and open_rows == 0, "items_fulfillments": len(ful),
                              "items_units": len(un), "items_codes": sum(len(i["code_hashes"]) for i in un)})
    cur.execute("rollback")
res["open_order_seen"] = any(not o["assembly_closed"] for o in res["orders"])
res["all_equal"] = all(o["signature_equal"] and o["assembly_closed"] == o["python_closed"] and o["items_fulfillments"] == o["carriers"] and o["items_units"] == o["units"]
                       and o["items_codes"] == o["codes"] for o in res["orders"]) and bool(res["orders"])
(OUT / "candidate-live.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1))
