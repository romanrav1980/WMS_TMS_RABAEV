"""C-0153: READ ONLY capture of live sources as restore scripts + SHA (CR removed, trailing newlines trimmed, upper hex)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
OUT = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_quality_posting")
OBJ = [("RRL_STOCK_EFFECT_CORE", "PACKAGE"), ("RRL_STOCK_EFFECT_CORE", "PACKAGE BODY"), ("RRL_STOCK_POSTING_API", "PACKAGE BODY"),
       ("RRL_TRADE_STOCK_GUARD", "PACKAGE BODY"), ("RRL_REGULATORY_STOCK_OUTBOX", "PACKAGE BODY"), ("RRL_TRADE_QUALITY_CASE_API", "PACKAGE"), ("RRL_TRADE_QUALITY_CASE_API", "PACKAGE BODY")]
hashes = {}
case_parts = []
with OracleGateway().transaction("C-0153 before sources READ ONLY") as cur:
    cur.execute("set transaction read only")
    for name, kind in OBJ:
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name, t=kind)
        text = "".join(r[0] for r in cur.fetchall()).replace("\r", "").rstrip("\n")
        hashes[f"{name}:{kind}"] = hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
        if name == "RRL_TRADE_QUALITY_CASE_API":  # spec+body in one restore file, like its C-0152 source
            case_parts.append("create or replace " + text + "\n/\n")
            continue
        fname = "before_" + name.lower() + ("_spec" if kind == "PACKAGE" else "") + ".sql"
        (OUT / fname).write_text("create or replace " + text + "\n/\n", encoding="utf-8", newline="\n")
    cur.execute("select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME like 'RRL_TRADE_QUALITY_CASE%' or OBJECT_NAME='RRL_STOCK_QUALITY_WRITEOFF' order by 1,2")
    print("quality objects live:", cur.fetchall())
    cur.execute("select MARK_STATE,count(*) from RRL_TRADE_STOCK_ATTR group by MARK_STATE"); print("MARK_STATE", cur.fetchall())
    cur.execute("select column_name,data_type from user_tab_columns where table_name='RRL_SAP_RECEIPT_OUTBOX' order by column_id"); print("outbox", cur.fetchall())
    cur.execute("select EVENT_TYPE,count(*) from RRL_SAP_RECEIPT_OUTBOX group by EVENT_TYPE order by 2 desc fetch first 8 rows only"); print("outbox types", cur.fetchall())
(OUT / "before_rrl_trade_quality_case_api.sql").write_text("".join(case_parts), encoding="utf-8", newline="\n")
(OUT / "before_hashes.json").write_text(json.dumps(hashes, indent=1) + "\n", encoding="utf-8")
print(json.dumps(hashes, indent=1))
