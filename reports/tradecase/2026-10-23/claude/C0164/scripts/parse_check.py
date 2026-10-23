"""C-0164 syntax check without DDL: the package body is compiled as an anonymous block (never executed: compilation fails on the not yet
existing tables). Expected: only semantic errors about RRL_TRADE_ORDER_COMPOSITION / RRL_TRADE_COMPOSITION_ACK, no PLS-00103 syntax error."""
import json, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway

s = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_composition_ack/002_composition_api.sql").read_text(encoding="utf-8").replace("\r\n", "\n")
body = s[s.index("create or replace package body RRL_TRADE_COMPOSITION_API as") + len("create or replace package body RRL_TRADE_COMPOSITION_API as"):]
body = body[:body.rindex("end;")]
block = "declare\n" + body + "begin null;\nend;"
with OracleGateway().transaction("C-0164 parse check READ ONLY") as cur:
    cur.execute("set transaction read only")
    try:
        cur.execute(block); msg = "COMPILED"
    except oracledb.DatabaseError as exc:
        msg = str(exc)
    cur.execute("rollback")
codes = sorted(set(re.findall(r"(PLS-\d+|ORA-\d+)", msg)))
res = {"codes": codes, "syntax_error": "PLS-00103" in codes, "message": msg[:3000]}
pathlib.Path(__file__).resolve().parents[1].joinpath("parse-check.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(res, indent=1, ensure_ascii=False))
