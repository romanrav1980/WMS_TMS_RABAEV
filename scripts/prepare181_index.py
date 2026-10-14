import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();folder="db/migrations/2026-10-11_ni042_sap_task_identity";out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select dbms_metadata.get_ddl('INDEX','RRL_WAREHOUSE_TASK_U2',user)from dual");old=q.fetchone()[0];old=old.read()if hasattr(old,"read")else old
 out[folder+"/000_before_index.sql"]=old.strip()+";\n"
out[folder+"/001_index.sql"]="""-- MIGRATION_ID:2026-10-11-181-sap-putaway-identity
-- Build replacement before dropping the old index; all non-SAP source keys unchanged.
create unique index RRL_WT_SOURCE_ID_I2 on RRL_WAREHOUSE_TASK
(TASK_SOURCE,nvl(SOURCE_TASK_ID,-1),nvl(SOURCE_MOVEMENT_ID,-1),TASK_TYPE,
 case when TASK_SOURCE='SAP_RECEIPT' then UID_PALLET else to_char(nvl(PARENT_TASK_ID,-1),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')end);
drop index RRL_WAREHOUSE_TASK_U2;
alter index RRL_WT_SOURCE_ID_I2 rename to RRL_WAREHOUSE_TASK_U2;
"""
out[folder+"/apply.sql"]="-- MIGRATION_ID:2026-10-11-181-sap-putaway-identity\n@@001_index.sql\n"
out[folder+"/rollback.sql"]="""-- Refuse restoring the incompatible historical key after multiple SAP putaway facts.
declare n number;begin
 select count(*)into n from(select SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,TASK_TYPE,PARENT_TASK_ID from RRL_WAREHOUSE_TASK
 group by TASK_SOURCE,SOURCE_TASK_ID,SOURCE_MOVEMENT_ID,TASK_TYPE,PARENT_TASK_ID having count(*)>1);
 if n>0 then raise_application_error(-20886,'OLD_TASK_IDENTITY_CANNOT_REPRESENT_CURRENT_HISTORY');end if;
end;
/
drop index RRL_WAREHOUSE_TASK_U2;
@@000_before_index.sql
"""
out[folder+"/verify.sql"]="select index_name,status,uniqueness from user_indexes where index_name='RRL_WAREHOUSE_TASK_U2';\nselect column_expression from user_ind_expressions where index_name='RRL_WAREHOUSE_TASK_U2';\n"
out[folder+"/checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-181-sap-putaway-identity","source_sha256":{p:hashlib.sha256(v.encode()).hexdigest()for p,v in out.items()},"recovery":"fresh index DDL, replacement built before removal, guarded rollback; no database copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
