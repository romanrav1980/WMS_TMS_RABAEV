"""C-0156: READ ONLY capture of RRL_STOCK_CASE_PICK_CMD body as restore script + SHA (CR removed, trailing newlines trimmed)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
OUT = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_case_pick_paper"); hashes = {}
with OracleGateway().transaction("C-0156 before source READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_PICK_CMD' and TYPE='PACKAGE BODY' order by LINE")
    text = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
    hashes["RRL_STOCK_CASE_PICK_CMD:PACKAGE BODY"] = hashlib.sha256(text.encode()).hexdigest().upper()
    (OUT / "before_rrl_stock_case_pick_cmd.sql").write_text("create or replace " + text + "\n/\n", encoding="utf-8", newline="\n")
    cur.execute("select count(*) from USER_OBJECTS where OBJECT_NAME='RRL_CASE_PICK_PAPER'"); print("paper pkg exists:", cur.fetchone()[0])
(OUT / "before_hashes.json").write_text(json.dumps(hashes, indent=1) + "\n", encoding="utf-8"); print(hashes)
