"""Checkpoint obsolete automatic receipt writers; scan receipt replaces them."""
import json
import re
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment

ROOT = Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0, str(ROOT / "api/wms_api_server"))
from app.config import get_settings
s = get_settings()
files = {}
old_sources = []
entrypoints = []
items = (
    ("RRL_ACCEPT_ORDER2", "PROCEDURE", "order_id int", "order_id"),
    ("RRL_ACCEPT_ORDER2_2", "PROCEDURE", "order_id int,user_id1 varchar2", "order_id,user_id1"),
    ("RRL_ACCEPT_ORDER2_3", "FUNCTION", "order_id int,user_id1 varchar2", "order_id,user_id1"),
    ("RRL_ACCEPT_ORDER3", "PROCEDURE", "order_id int,user_id1 varchar2", "order_id,user_id1"),
    ("RRL_OTKAT_ORDER2", "PROCEDURE", "order_id int", "order_id"),
)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as conn:
    cur = conn.cursor()
    cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
    if cur.fetchone() != ("RABAEV", "orcl"):
        raise RuntimeError("Unexpected target")
    cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if cur.fetchone() != ("PREPARED",):
        raise RuntimeError("Preparation requires PREPARED")
    for name, kind, args, call in items:
        cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE", n=name,t=kind)
        original = "".join(row[0] for row in cur)
        if not original or "SAP_SCANNED_RECEIPT_REQUIRED" in original:
            raise RuntimeError("Expected original " + name)
        files["147_" + name.lower() + "_rollback.sql"] = "create or replace " + original.rstrip() + "\n/\n"
        old = re.sub(r"\b" + name + r"\b",name + "_SP_OLD",original,flags=re.I)
        if kind == "FUNCTION":
            old = re.sub(r"(return\s+int\s*)(is\b)",r"\1accessible by(function " + name + r") \2",old,count=1,flags=re.I)
        else:
            old = re.sub(r"(\)\s*)(as\b)",r"\1accessible by(procedure " + name + r") \2",old,count=1,flags=re.I)
        if "accessible by" not in old:
            raise RuntimeError("Restricted declaration not located: " + name)
        old = re.sub(r"--[^\r\n]*","",old)
        old_sources.append("create or replace " + old.rstrip() + "\n/\n")
        signature = (" return int" if kind == "FUNCTION" else "") + " authid definer"
        fallback = ("return " if kind == "FUNCTION" else "") + name + "_SP_OLD(" + call + ");"
        if kind == "PROCEDURE":
            fallback += "return;"
        entrypoints.append(f"""create or replace {kind.lower()} {name}({args}){signature} is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then {fallback} end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'SAP_SCANNED_RECEIPT_REQUIRED: use receiving.html?receipt_document_id='||to_char(order_id,'TM9')||'; reverse physical receipt with RRL_STORNO_ORDER3');
end;
/
""")
files["147_receipt_legacy.sql"] = "\n".join(old_sources)
files["147_receipt_entrypoints.sql"] = "\n".join(entrypoints)
files["147_receipt_retirement_apply.sql"] = "@@147_receipt_legacy.sql\n@@147_receipt_entrypoints.sql\n@@014b_recompile.sql\n"
files["147_receipt_retirement_rollback.sql"] = (
    "declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;"
    "if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;\n/\n" +
    "\n".join("@@147_" + name.lower() + "_rollback.sql" for name,_,_,_ in items) + "\n@@014b_recompile.sql\n"
)
print(json.dumps(files,ensure_ascii=True))
