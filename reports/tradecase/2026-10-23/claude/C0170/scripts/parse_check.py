"""C-0170 syntax check without DDL: the candidate guard body compiled as an anonymous block (never executed). Expected only semantic
errors from accessible-by callees (PLS-00904), no PLS-00103."""
import json, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
s = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_short_guard/001_guard_body.sql").read_text(encoding="utf-8")
head = re.match(r"create or replace package body \w+ as", s); body = s[head.end():s.rindex("end;")]
with OracleGateway().transaction("C-0170 parse READ ONLY") as cur:
    cur.execute("set transaction read only")
    try: cur.execute("declare\n" + body + "begin null;\nend;"); msg = "COMPILED"
    except oracledb.DatabaseError as exc: msg = str(exc)
    cur.execute("rollback")
codes = sorted(set(re.findall(r"(PLS-\d+|ORA-\d+)", msg)))
res = {"codes": codes, "syntax_error": "PLS-00103" in codes, "message": msg[:2000]}
pathlib.Path(__file__).resolve().parents[1].joinpath("parse-check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: res[k] for k in ("codes", "syntax_error")}))
