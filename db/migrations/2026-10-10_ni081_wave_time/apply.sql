@@001_schema.sql
@@002_api.sql
@@003_guard.sql
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_WAVE_TIME_API','RRL_WAVE_TIME_PLAN_GUARD','RRL_STOCK_POSTING_API')and STATUS!='VALID';
 if n!=0 then raise_application_error(-20899,'WAVE_TIME140_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-140-approved-existing-wave-time' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Approved aware existing wave window/legacy planned wall time/stale version/replay/no stock',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
