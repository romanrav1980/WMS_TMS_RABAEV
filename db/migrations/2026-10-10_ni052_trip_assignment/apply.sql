@@002_context.sql
@@001_assignment.sql
@@003_membership_guard.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_TT_ADD_PALL' and OBJECT_TYPE='FUNCTION' and STATUS='VALID';
if n!=1 then raise_application_error(-20808,'TRIP_ASSIGNMENT_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-080-trip-assignment-serialization' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing ST writer serializes sorted TT then actual ST membership; visible failures and loaded protections',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
