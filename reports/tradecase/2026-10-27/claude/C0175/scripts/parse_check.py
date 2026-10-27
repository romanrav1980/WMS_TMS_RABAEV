"""C-0175 syntax check without DDL: each candidate body compiled as an anonymous block (never executed); no PLS-00103 expected."""
import json, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
KIT = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-27_trade_order_units")
res = {}
with OracleGateway().transaction("C-0175 parse READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name in ("001_document_api_body.sql", "002_order_api_body.sql", "before_document_api_body.sql", "before_order_api_body.sql"):
        s = (KIT / name).read_text(encoding="utf-8")
        head = re.match(r"create or replace package body \w+ as\n", s); body = s[head.end():s.rindex("end;")]
        try:
            cur.execute("declare\n" + body + "begin null;\nend;"); msg = "COMPILED"
        except oracledb.DatabaseError as exc:
            msg = str(exc)
        codes = sorted(set(re.findall(r"(PLS-\d+|ORA-\d+)", msg)))
        res[name] = {"codes": codes, "syntax_error": "PLS-00103" in codes, "message": msg[:800]}
    cur.execute("rollback")
pathlib.Path(__file__).resolve().parents[1].joinpath("parse-check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: (v["codes"], v["syntax_error"]) for k, v in res.items()}))
