"""C-0157: READ ONLY dump of live sources relevant to topup into the common pool (SHIP_FROM_STOCK), with SHA as in preflight."""
import hashlib, json, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
OUT = pathlib.Path(__file__).parent.parent / "src"
names = sys.argv[1:]
with OracleGateway().transaction("C-0157 source dump READ ONLY") as cur:
    cur.execute("set transaction read only")
    if not names:
        cur.execute("select distinct name,type from user_source where upper(text) like '%SHIP_FROM_STOCK%' order by 1,2"); print("SHIP_FROM_STOCK in:", cur.fetchall())
        cur.execute("select distinct name,type from user_source where upper(text) like '%COMMON_POOL%' order by 1,2"); print("COMMON_POOL in:", cur.fetchall())
    shas = {}
    for n in names:
        cur.execute("select type,text from user_source where name=:n order by type,line", n=n.upper())
        by = {}
        for t, x in cur.fetchall(): by.setdefault(t, []).append(x)
        for t, lines in by.items():
            text = "".join(lines).replace("\r", "").rstrip("\n")
            (OUT / f"{n.upper()}.{t.replace(' ', '_')}.sql").write_text(text, encoding="utf-8")
            shas[f"{n.upper()}:{t}"] = hashlib.sha256(text.encode()).hexdigest().upper()
    if shas: print(json.dumps(shas, indent=1))
