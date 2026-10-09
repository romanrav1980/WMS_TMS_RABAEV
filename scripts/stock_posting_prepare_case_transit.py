"""Checkpoint only the configuration rows this setup can add; never copy the database."""
import json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment();sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if q.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if q.fetchone()!=("PREPARED",):raise RuntimeError("Setup requires PREPARED")
 q.execute("select ID from RRL_WARES where ID>0 order by ID fetch first 201 rows only")
 warehouses=[int(row[0]) for row in q]
 if len(warehouses)>200:raise RuntimeError("Transit setup warehouse bound exceeded")
 new=[];existing=[]
 for ware in warehouses:
  cell="CPT_"+str(ware)
  q.execute("select WARE_ID,IS_SYSTEM,BLOCKED_FOR_REMAINS from RRL_CELLS where CELL=:c",c=cell)
  rows=q.fetchall()
  if rows:existing.append({"cell":cell,"rows":rows})
  else:new.append(cell)
cp=ROOT/"runtime/stock_posting_20261008/165_short_transit-checkpoint"
cp.mkdir(parents=True,exist_ok=False)
(cp/"rows.json").write_text(json.dumps({"warehouses":warehouses,"new_cells":new,"existing":existing}),encoding="utf-8")
rollback="declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_TRANSIT_ROLLBACK');end if;RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');\n"
for cell in new:
 rollback+="delete from RRL_CELLS where CELL='"+cell+"' and not exists(select 1 from RRL_REMAINS s where s.CELL='"+cell+"');\n"
rollback+="RRL_STOCK_CONFIG_API.end_change;commit;exception when others then rollback;RRL_STOCK_CONFIG_API.end_change;raise;end;\n/\n"
print(json.dumps({"165_case_transit_rollback.sql":rollback},ensure_ascii=True))
