-- MIGRATION_ID: 2026-10-15-warehouse-scale-requests
@@before.sql
@@schema.sql
@@body.sql
@@wh_scale_api.sql
@@assembly_body.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_WH_WEIGH_REQUEST_API','RRL_WH_WEIGH_REQUEST_GUARD','RRL_WH_WEIGH_CLAIM_GUARD','RRL_WH_SCALE_API','RRL_ASSEMBLY_SCALE_API');
 if n!=0 then raise_application_error(-20886,'WH_WEIGH_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'WH_WEIGH_GLOBAL_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-warehouse-scale-requests'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user,d.SCRIPT_NAME='apply.sql',d.ROLLBACK_SCRIPT='rollback.sql' where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Mass-free warehouse scale requests, bounded sender claims, current CASE/source guards',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;


