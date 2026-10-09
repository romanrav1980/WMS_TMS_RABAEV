declare n number;
begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_INTERNAL_CMD','RRL_STOCK_NATIVE_API','RRL_STOCK_PALLET_UOM','RRL_STOCK_TRANSFER_CORE','RRL_STOCK_POSTING_API')
 and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=10 then raise_application_error(-20808,'INTERNAL_COMMAND_PACKAGES_NOT_VALID');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_JOURNAL_GUARD' and STATUS='VALID';
 if n!=1 then raise_application_error(-20808,'JOURNAL_GUARD_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-026-native-internal-command' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Native whole-operation runner and internal movement; combined TYPE2 guard fixed; still PREPARED',sysdate,user,'066_internal_move_apply.sql','066_internal_move_rollback.sql','APPLIED');
commit;
