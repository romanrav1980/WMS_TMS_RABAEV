"""C-0173 syntax check without DDL: each candidate body compiled as an anonymous block (never executed), with the candidate function
as a local subprogram after the package globals. Expected only semantic errors (accessible-by callees PLS-00904, a local function
inside SQL PLS-00231), no PLS-00103. The function itself was compiled and executed READ ONLY by tests/tradecase/live_trade_recipient_version.py."""
import json, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
KIT = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-27_trade_recipient_version")
function = (KIT / "001_function.sql").read_text(encoding="utf-8")
function = function[len("create or replace "):function.rindex("\n/")]
res = {}
with OracleGateway().transaction("C-0173 parse READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name in ("002_pick_context_body.sql", "003_transport_core_body.sql"):
        s = (KIT / name).read_text(encoding="utf-8")
        head = re.match(r"create or replace package body \w+ as\n", s); body = s[head.end():s.rindex("end;")]
        first, rest = body.split("\n", 1) if name.startswith("002") else ("", body)
        try:
            cur.execute("declare\n" + first + "\n " + function + "\n" + rest + "begin null;\nend;"); msg = "COMPILED"
        except oracledb.DatabaseError as exc:
            msg = str(exc)
        codes = sorted(set(re.findall(r"(PLS-\d+|ORA-\d+)", msg)))
        res[name] = {"codes": codes, "syntax_error": "PLS-00103" in codes, "message": msg[:1500]}
    cur.execute("rollback")
pathlib.Path(__file__).resolve().parents[1].joinpath("parse-check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: (v["codes"], v["syntax_error"]) for k, v in res.items()}))
