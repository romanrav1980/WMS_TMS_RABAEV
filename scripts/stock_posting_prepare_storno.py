"""Export the existing native receipt reversal and restrict its PREPARED fallback."""
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
with oracledb.connect(user=s.oracle_user, password=s.oracle_password, dsn=s.oracle_dsn) as c:
    q = c.cursor()
    q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
    if q.fetchone() != ("RABAEV", "orcl"):
        raise RuntimeError("Unexpected target")
    q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if q.fetchone() != ("PREPARED",):
        raise RuntimeError("Preparation requires PREPARED")
    q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORNO_ORDER3' and TYPE='PROCEDURE' order by LINE")
    original = "".join(row[0] for row in q)
    if not original or "RRL_STOCK_NATIVE_API" in original:
        raise RuntimeError("Expected original native procedure")
    old = re.sub(r"\bRRL_STORNO_ORDER3\b", "RRL_STORNO_ORDER3_SP_OLD", original, flags=re.I)
    old = re.sub(r"\)\s*as\b", ") accessible by(procedure RRL_STORNO_ORDER3) as", old, count=1, flags=re.I)
    if "accessible by" not in old:
        raise RuntimeError("Restricted legacy declaration not located")
    # Comments are not runtime behavior; retain source bytes in paired rollback.
    old = re.sub(r"--[^\r\n]*", "", old)
    print(json.dumps({
        "132_storno_legacy.sql": "create or replace " + old.rstrip() + "\n/\n",
        "132_storno_native_rollback.sql": "create or replace " + original.rstrip() + "\n/\n",
    }, ensure_ascii=True))
