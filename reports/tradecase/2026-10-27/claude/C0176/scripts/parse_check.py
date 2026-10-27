"""C-0176 syntax check without DDL: candidate sources compiled inside anonymous blocks (never executed). The journal table does not
exist before apply, so only semantic errors (PLS-00201/ORA-00942) are expected for the body; no PLS-00103."""
import json, pathlib, re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
KIT = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-27_tt_selected_places")
def body_of(name):
    s = (KIT / name).read_text(encoding="utf-8"); return s[len("create or replace "):s.rindex("\n/")]
writer = body_of("002_writer.sql")
package = body_of("004_removal_body.sql"); package = package[package.index(" as\n") + 4:package.rindex("end;")]
blocks = {"002_writer.sql": "declare r varchar2(1024);\n " + writer + "\nbegin null;\nend;",
          "004_removal_body.sql": "declare\n" + package + "begin null;\nend;"}
res = {}
with OracleGateway().transaction("C-0176 parse READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, block in blocks.items():
        try:
            cur.execute(block); msg = "COMPILED"
        except oracledb.DatabaseError as exc:
            msg = str(exc)
        codes = sorted(set(re.findall(r"(PLS-\d+|ORA-\d+)", msg)))
        res[name] = {"codes": codes, "syntax_error": "PLS-00103" in codes, "message": msg[:900]}
    cur.execute("rollback")
pathlib.Path(__file__).resolve().parents[1].joinpath("parse-check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: (v["codes"], v["syntax_error"]) for k, v in res.items()}))
