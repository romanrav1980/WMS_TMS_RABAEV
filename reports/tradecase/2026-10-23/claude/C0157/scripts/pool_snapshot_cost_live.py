"""C-0157 SQL cost: pool snapshot before/after on the (warehouse, article) pairs with the most open order rows (READ ONLY anonymous
blocks; the candidate adds RRL_TRADE_TOPUP_ADOPT.line_proposal per open row). Three runs each, ms; outputs must be identical."""
import hashlib, json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
M = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_topup_common_pool")


def snap_fn(file):
    s = (M / file).read_text(encoding="utf-8")
    return s[s.index(" function snapshot_json"):s.index("\nend;")].replace(
        "x:=json_object_t.parse(line_snapshot_json(", "x:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(")


out = []
with OracleGateway().transaction("C-0157 pool snapshot cost READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("""select nvl(r.WARE_ID,h.WARE_ID) W,r.ARTICUL,count(*) N from RRL_CUSTOMER_ORDER_ROW r join RRL_CUSTOMER_ORDER h on h.CUSTOMER_ORDER_ID=r.CUSTOMER_ORDER_ID
      where h.STATUS in('IMPORTED','OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK') and r.STATUS in('OPEN','PLANNED_FULL','PLANNED_PARTIAL','NO_STOCK') and r.ORDER_QTY>0
      group by nvl(r.WARE_ID,h.WARE_ID),r.ARTICUL order by 3 desc fetch first 3 rows only""")
    for ware, art, n in cur.fetchall():
        row = {"warehouse": ware, "article": art, "open_rows": n}
        for name, file in (("before", "before_rrl_stock_pool_read.sql"), ("after", "001_pool_read.sql")):
            block = "declare\n" + snap_fn(file) + "\nbegin :o:=snapshot_json(:w,:a);end;"
            times, sha = [], None
            for _ in range(3):
                v = cur.var(oracledb.DB_TYPE_CLOB); t = time.perf_counter()
                try:
                    cur.execute(block, o=v, w=ware, a=art); sha = hashlib.sha256(v.getvalue().read().encode()).hexdigest()
                except oracledb.DatabaseError as e:
                    sha = str(e.args[0]).split("\n")[0]
                times.append(round((time.perf_counter() - t) * 1000, 1))
            row[name] = {"ms": times, "result": sha}
        row["same_result"] = row["before"]["result"] == row["after"]["result"]
        out.append(row); print(row)
pathlib.Path(__file__).parent.parent.joinpath("pool-snapshot-cost-live.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
