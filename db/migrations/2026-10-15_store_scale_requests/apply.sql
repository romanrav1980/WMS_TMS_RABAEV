@@before.sql
-- MIGRATION_ID: 2026-10-15-store-scale-requests
@@schema.sql
@@body.sql
declare n number;
begin
 select count(*) into n from user_errors where name in('RRL_STORE_WEIGH_API','RRL_STORE_WEIGH_GUARD');
 if n!=0 then raise_application_error(-20886,'STORE_WEIGH_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-15-store-scale-requests' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Mass-free store scale request handshake; equipment remains sole capture writer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
