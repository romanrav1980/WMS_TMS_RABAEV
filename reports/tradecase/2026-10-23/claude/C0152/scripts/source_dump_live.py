"""C-0152: READ ONLY dump of a native package body to the scratch report folder (no writes to Oracle)."""
import sys, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
with OracleGateway().transaction("C-0152 source dump READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name in sys.argv[2:]:
        for kind in ("PACKAGE", "PACKAGE BODY"):
            cur.execute("select text from user_source where name=:n and type=:t order by line", n=name, t=kind)
            text = "".join(r[0] for r in cur.fetchall())
            if text: (out / f"{name}.{kind.replace(' ', '_').lower()}.sql").write_text(text, encoding="utf-8")
            print(name, kind, len(text))
