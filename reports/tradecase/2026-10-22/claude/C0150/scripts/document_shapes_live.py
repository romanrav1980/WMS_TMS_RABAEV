"""C-0150: READ ONLY shapes of accepted TRIP/ORDER bodies (keys only, no values, no writes)."""
import json, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
def keys(v, depth=0):
    if isinstance(v, dict): return {k: keys(x, depth + 1) for k, x in v.items()} if depth < 3 else "{...}"
    if isinstance(v, list): return [keys(v[0], depth + 1)] if v else []
    return type(v).__name__
with OracleGateway().transaction("C-0150 document shapes READ ONLY") as cur:
    cur.execute("set transaction read only")
    for kind in ("TRIP", "ORDER"):
        cur.execute("select WARE_ID,BODY_JSON from RRL_TRADE_DOCUMENT where ENTITY_TYPE=:k and STATUS='ACCEPTED' order by VERSION_NO desc fetch first 1 rows only", k=kind)
        r = cur.fetchone()
        body = json.loads(r[1].read() if hasattr(r[1], "read") else r[1])
        print(kind, r[0], json.dumps(keys(body), ensure_ascii=False))
    cur.execute("select count(*) from(select WARE_ID,EXTERNAL_ID from RRL_TRADE_DOCUMENT where ENTITY_TYPE in('TRIP','ORDER') and STATUS='ACCEPTED' group by ENTITY_TYPE,WARE_ID,EXTERNAL_ID having count(*)>1)")
    print("ids with several ACCEPTED versions", cur.fetchone()[0])
    for t in ("RRL_TRADE_DOCUMENT", "RRL_TRADE_TRIP_LINK"):
        cur.execute("select column_name from user_tab_columns where table_name=:t order by column_id", t=t)
        print(t, [c[0] for c in cur.fetchall()])
