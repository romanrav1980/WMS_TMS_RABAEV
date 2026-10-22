"""C-0149: READ ONLY excerpt of the owner guard and access check used by the yard API (no writes)."""
import sys, re
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0149 guard source READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, pat in [("RRL_TRADE_STOCK_GUARD", r"assert_owner|owner_allowed|raise_application_error|RUSERS"), ("RRL_ACCESS_API", r"function allowed|RUSERS|ACTIVE|DISABLED|LOCKED")]:
        cur.execute("select line,text from user_source where name=:n and type='PACKAGE BODY' order by line", n=name)
        rows = cur.fetchall()
        hits = [l for l, t in rows if re.search(pat, t, re.I)]
        shown = set()
        for l in hits[:12]:
            for ll, t in rows:
                if l - 1 <= ll <= l + 3 and ll not in shown:
                    shown.add(ll); print(name, ll, t.rstrip()[:200])
