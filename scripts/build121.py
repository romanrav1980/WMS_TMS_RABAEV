from pathlib import Path
import json,re,sys,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();base=Path("db/migrations/2026-10-08_stock_posting_core");dest="db/migrations/2026-10-10_ni061_custody/";out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_TT_HU_LOAD_FACT_GUARD'and TYPE='TRIGGER'order by LINE")
 old="create or replace "+"".join(row[0] for row in q).rstrip()+"\n/\n"
old=old.replace(chr(13)+chr(10),chr(10))
out[str(base/"439_before121_load_fact_guard.sql")]=old
needle=" elsif kind_name!='TRIP_DEPART'"
assert needle in old
branch=""" elsif kind_name='INTERWARE_CUSTODY_RELEASE' then
  if :old.STATUS!='DEPARTED' or :new.STATUS!=:old.STATUS or :old.CUSTODY_RELEASED_AT is not null or :old.CUSTODY_RELEASE_OPERATION_ID is not null or :new.CUSTODY_RELEASED_AT is null or :new.CUSTODY_RELEASE_OPERATION_ID is null or :new.CUSTODY_RELEASE_OPERATION_ID!=op then raise_application_error(-20863,'INTERWARE_CUSTODY_RELEASE_REQUIRED');end if;
  if :new.LOAD_OPERATION_ID!=:old.LOAD_OPERATION_ID or :new.TT_ID!=:old.TT_ID or nvl(:new.ROOT_UID,chr(0))!=nvl(:old.ROOT_UID,chr(0))or nvl(:new.ROOT_CASE_TASK_ID,-1)!=nvl(:old.ROOT_CASE_TASK_ID,-1)or :new.VEHICLE_ID!=:old.VEHICLE_ID or :new.VEHICLE_NUMBER!=:old.VEHICLE_NUMBER or :new.DOCK!=:old.DOCK or :new.WARE_ID!=:old.WARE_ID or :new.GROSS_WEIGHT_KG!=:old.GROSS_WEIGHT_KG or :new.BOUNDING_VOLUME_M3!=:old.BOUNDING_VOLUME_M3 or :new.CONTENT_VERSION!=:old.CONTENT_VERSION or :new.LOADED_BY!=:old.LOADED_BY or :new.LOADED_AT!=:old.LOADED_AT or :new.DEPARTURE_OPERATION_ID!=:old.DEPARTURE_OPERATION_ID or :new.DEPARTED_AT!=:old.DEPARTED_AT or dbms_lob.compare(:new.COMPOSITION_JSON,:old.COMPOSITION_JSON)!=0 then raise_application_error(-20863,'INTERWARE_DEPARTURE_HISTORY_IMMUTABLE');end if;
  declare n number;begin
   select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF f join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=f.RECEIPT_OPERATION_ID join RRL_INTERWARE_UNLOAD u on u.OPERATION_ID=r.UNLOAD_OPERATION_ID where f.OPERATION_ID=op and r.SOURCE_LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID and r.ROOT_UID=:old.ROOT_UID and :new.CUSTODY_RELEASED_AT=u.CREATED_AT;
   if n!=1 then raise_application_error(-20863,'INTERWARE_ACTUAL_CUSTODY_PROOF_REQUIRED');end if;
  end;
"""
guard=old.replace(needle,branch+needle,1).replace("if inserting then\n","if inserting then\n  if :new.CUSTODY_RELEASED_AT is not null or :new.CUSTODY_RELEASE_OPERATION_ID is not null then raise_application_error(-20863,'NEW_LOAD_CANNOT_HAVE_RELEASED_CUSTODY');end if;\n",1)
# Neither TRIP_DEPART nor other old branch may forge release columns.
guard=guard.replace(" or :new.LOADED_BY!=:old.LOADED_BY", " or nvl(:new.CUSTODY_RELEASE_OPERATION_ID,chr(0))!=nvl(:old.CUSTODY_RELEASE_OPERATION_ID,chr(0)) or :new.CUSTODY_RELEASED_AT is not null\n  or :new.LOADED_BY!=:old.LOADED_BY",1) if False else guard
guard=guard.replace(" elsif kind_name!='TRIP_DEPART'"," elsif :new.CUSTODY_RELEASED_AT is not null or :new.CUSTODY_RELEASE_OPERATION_ID is not null or kind_name!='TRIP_DEPART'",1)
out[dest+"003_load_guard.sql"]=guard
root=(base/"438_before121_root.sql").read_text(encoding="utf-8");root=re.sub(r"\n\s*\n","\n",root)
root=root.replace("  elsif g_kind='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.compile_command","  elsif g_kind='INTERWARE_CUSTODY_RELEASE' then RRL_STOCK_INTERWARE_CUSTODY.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  elsif g_kind='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.compile_command",1)
root=root.replace("  elsif g_kind='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.execute_command","  elsif g_kind='INTERWARE_CUSTODY_RELEASE' then RRL_STOCK_INTERWARE_CUSTODY.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='INTERWARE_PUTAWAY_PLAN' then RRL_STOCK_INTERWARE_PUT.execute_command",1)
assert root.count("RRL_STOCK_INTERWARE_CUSTODY")==2;out[dest+"004_root.sql"]=root
out[dest+"001_schema.sql"]="""begin execute immediate 'alter table RRL_TT_HU_LOAD_FACT add(CUSTODY_RELEASED_AT timestamp with time zone,CUSTODY_RELEASE_OPERATION_ID varchar2(100)references RRL_STOCK_OPERATION(OPERATION_ID))';exception when others then if sqlcode!=-1430 then raise;end if;end;
/
begin execute immediate q'[create table RRL_INTERWARE_CUSTODY_PROOF(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 SOURCE_LOAD_OPERATION_ID varchar2(100) not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[dest+"005_active_index.sql"]="""begin execute immediate 'drop index RRL_TT_HU_LOAD_UID_U1';exception when others then if sqlcode!=-1418 then raise;end if;end;
/
create unique index RRL_TT_HU_LOAD_UID_U1 on RRL_TT_HU_LOAD_FACT(case when STATUS in('LOADED','DEPARTED')and CUSTODY_RELEASED_AT is null then ROOT_UID end);
/
"""
out[dest+"006_proof_guard.sql"]="""create or replace trigger RRL_INTERWARE_CUSTODY_GUARD before insert or update or delete on RRL_INTERWARE_CUSTODY_PROOF for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_CUSTODY_PROOF_IMMUTABLE');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_CUSTODY_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='INTERWARE_CUSTODY_RELEASE'and STATE='IN_FLIGHT'and ACTOR=:new.ACTOR and json_value(RESOLVED_PLAN_JSON,'$.domain.receipt_operation_id')=:new.RECEIPT_OPERATION_ID and json_value(RESOLVED_PLAN_JSON,'$.domain.source_load_operation_id')=:new.SOURCE_LOAD_OPERATION_ID;
 if n!=1 then raise_application_error(-20863,'INTERWARE_CUSTODY_RESOLVED_PROOF_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_INTERWARE_CUSTODY_PROOF',op));
end;
/
"""
out[dest+"apply.sql"]="""@@001_schema.sql
@@002_command.sql
@@003_load_guard.sql
@@004_root.sql
@@005_active_index.sql
@@006_proof_guard.sql
declare n number;begin select count(*)into n from user_objects where OBJECT_NAME in('RRL_STOCK_INTERWARE_CUSTODY','RRL_STOCK_POSTING_API','RRL_TT_HU_LOAD_FACT_GUARD','RRL_INTERWARE_CUSTODY_GUARD','RRL_TT_HU_LOAD_UID_U1')and STATUS!='VALID';if n!=0 then raise_application_error(-20899,'INTERWARE121_INVALID_OBJECTS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-121-interwarehouse-first-leg-custody-release' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Explicit native custody release on actual target receipt while preserving original departure history and active UID uniqueness',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
"""
out[dest+"rollback.sql"]="""declare n number;begin select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF;if n!=0 then raise_application_error(-20899,'INTERWARE121_FORWARD_ONLY_AFTER_FACTS');end if;end;
/
@@../2026-10-08_stock_posting_core/438_before121_root.sql
@@../2026-10-08_stock_posting_core/439_before121_load_fact_guard.sql
drop index RRL_TT_HU_LOAD_UID_U1;
create unique index RRL_TT_HU_LOAD_UID_U1 on RRL_TT_HU_LOAD_FACT(case when STATUS in('LOADED','DEPARTED')then ROOT_UID end);
drop table RRL_INTERWARE_CUSTODY_PROOF;
alter table RRL_TT_HU_LOAD_FACT drop(CUSTODY_RELEASED_AT,CUSTODY_RELEASE_OPERATION_ID);
drop package RRL_STOCK_INTERWARE_CUSTODY;
"""
print(json.dumps(out,ensure_ascii=True))
