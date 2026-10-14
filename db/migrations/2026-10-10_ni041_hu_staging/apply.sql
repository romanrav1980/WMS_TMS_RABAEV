@@001_slot.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_HU_SLOT' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=2 then raise_application_error(-20808,'HU_STAGING_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-057-hu-case-staging' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Closed CASE-only HU reuses existing system control/staging target policy; ordinary stock still excluded',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
