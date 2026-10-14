@@001_schema.sql
@@002_slot.sql
@@003_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_SLOT','RRL_STOCK_HU_CMD') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=4 then raise_application_error(-20808,'MULTI_HU_SLOTS_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-068-multi-hu-slots' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Several measured top HUs in distinct storage slots; aggregate current+planned cell load; existing claim composition version',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
