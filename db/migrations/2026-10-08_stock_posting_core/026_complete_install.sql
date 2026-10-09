declare n number;
begin
 select count(*) into n from user_objects where OBJECT_NAME in(
 'RRL_STOCK_LOCK_API','RRL_STOCK_CTX_API','RRL_STOCK_BALANCE_CORE','RRL_STOCK_OPERATION_CORE',
 'RRL_STOCK_RESERVE_CORE','RRL_STOCK_LOCATION_CORE','RRL_STOCK_COMMAND_PLAN','RRL_STOCK_MOVE_CORE',
 'RRL_STOCK_POSTING_API') and STATUS!='VALID';
 if n!=0 then raise_application_error(-20808,'STOCK_RUNTIME_COMPILATION_FAILED'); end if;
 select count(*) into n from user_objects where OBJECT_NAME in(
 'RRL_STOCK_LOCK_API','RRL_STOCK_CTX_API','RRL_STOCK_BALANCE_CORE','RRL_STOCK_OPERATION_CORE',
 'RRL_STOCK_RESERVE_CORE','RRL_STOCK_LOCATION_CORE','RRL_STOCK_COMMAND_PLAN','RRL_STOCK_MOVE_CORE',
 'RRL_STOCK_POSTING_API') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY');
 if n!=18 then raise_application_error(-20808,'STOCK_RUNTIME_INCOMPLETE'); end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-016-stock-command-runtime' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Dormant posting coordinator and bounded manual move; PREPARED, no cutover',
sysdate,user,'026_complete_install.sql','026_rollback.sql','APPLIED');
commit;
