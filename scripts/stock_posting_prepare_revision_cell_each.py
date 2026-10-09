"""Checkpoint indirect EA inventory and replace its implicit multi-lot deduction."""
import json,re,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
root=Path(__file__).resolve().parents[1];d=root/"db/migrations/2026-10-08_stock_posting_core"
load_local_oracle_environment();sys.path.insert(0,str(root/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if q.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if q.fetchone()!=("PREPARED",):raise RuntimeError("Expected PREPARED")
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_REVIZION_CELL' and TYPE='FUNCTION' order by LINE")
 source="".join(r[0] for r in q)
 if not source or "RRL_STOCK_INV_ENTRY" in source:raise RuntimeError("Expected original")
 cp=root/"runtime/stock_posting_20261008/193_revision-cell-original-checkpoint";cp.mkdir(exist_ok=True)
 (cp/"RRL_REVIZION_CELL.sql").write_text("create or replace "+source+"\n/\n",encoding="utf-8")
old=re.sub(r"\bRRL_REVIZION_CELL\b","RRL_REVIZION_CELL_SP_OLD",source,flags=re.I)
old=re.sub(r"return\s+varchar2", "return varchar2 accessible by(function RRL_REVIZION_CELL)",old,count=1,flags=re.I)
old=re.sub(r"--[^\r\n]*","",old)
out={}
out[str(d/"193_revision_cell_each_legacy.sql")]="create or replace "+old.rstrip()+"\n/\n"
out[str(d/"193_revision_cell_each_entry.sql")]= """create or replace function RRL_REVIZION_CELL(
 CELL1 varchar2,count1 number,user_id1 varchar2,
 p_operation_id varchar2 default null,p_revision_id number default null,
 p_uid varchar2 default null,p_reason varchar2 default null) return varchar2 authid definer is
 state varchar2(20);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return RRL_REVIZION_CELL_SP_OLD(CELL1,count1,user_id1);end if;
 return RRL_STOCK_INV_ENTRY.count_lot(CELL1,p_uid,RRL_STOCK_PLAN_HELPER.decimal_text(count1),
  'EA',p_revision_id,user_id1,p_operation_id,p_reason);
end;
/
"""
out[str(d/"193_revision_cell_each_rollback.sql")]="declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;\n/\ncreate or replace "+source.rstrip()+"\n/\n"
p=d/"136_inventory_native_api.sql";text=p.read_text(encoding="utf-8")
needle="accessible by(function RRL_REVIZION_CELL_KOR,"
assert text.count(needle)==1
out[str(p)]=text.replace(needle,"accessible by(function RRL_REVIZION_CELL,function RRL_REVIZION_CELL_KOR,",1)
out[str(d/"193_revision_cell_each_apply.sql")]="@@193_revision_cell_each_legacy.sql\n@@193_revision_cell_each_entry.sql\n@@136_inventory_native_api.sql\n@@014b_recompile.sql\n"
print(json.dumps({str(Path(k).relative_to(root)):v for k,v in out.items()},ensure_ascii=True))
