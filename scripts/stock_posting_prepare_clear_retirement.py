"""Remove an already-disabled UI's destructive pseudo-inventory function."""
import hashlib,json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1];load_local_oracle_environment();sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();base="db/migrations/2026-10-08_stock_posting_core/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as conn:
 cur=conn.cursor();cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if cur.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if cur.fetchone()!=("PREPARED",):raise RuntimeError("Dormant preparation only")
 cur.execute("select TEXT from USER_SOURCE where NAME='RRL_CLEAR_OTBOR_CELL' and TYPE='FUNCTION' order by LINE")
 original="create or replace "+"".join(row[0] for row in cur).rstrip()+"\n/\n"
 if "INVENTORY_MEASURED_COUNT_REQUIRED" in original:raise RuntimeError("Already retired")
cp=ROOT/"runtime/stock_posting_20261008/176_clear-original-checkpoint";cp.mkdir(parents=True,exist_ok=False)
(cp/"source.sql").write_text(original,encoding="utf-8")
(cp/"manifest.json").write_text(json.dumps({"original_sha256":hashlib.sha256(original.encode()).hexdigest()}),encoding="utf-8")
sql="""create or replace function RRL_CLEAR_OTBOR_CELL(CELL1 varchar2,user_id1 varchar2) return varchar2 authid definer is
begin
 if CELL1 is null or user_id1 is null or RRL_HAS_WRIGHT(user_id1,'stock_inventory_count')!=1 then
  raise_application_error(-20882,'INVENTORY_COUNT_FORBIDDEN');
 end if;
 raise_application_error(-20886,'INVENTORY_MEASURED_COUNT_REQUIRED: inventory-count.html; no automatic lot deletion');
end;
/
"""
rollback="declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;\n/\n"+original+"\n@@014b_recompile.sql\n"
print(json.dumps({base+"176_clear_entrypoint.sql":sql,base+"176_clear_retirement_apply.sql":"@@176_clear_entrypoint.sql\n@@014b_recompile.sql\n",base+"176_clear_retirement_rollback.sql":rollback},ensure_ascii=True))
