-- MIGRATION_ID: 2026-10-15-stock-operation-clock
@@schema.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_STOCK_CLOCK_GUARD','RRL_STOCK_APPLIED_CLOCK');
 if n!=0 then raise_application_error(-20886,'STOCK_CLOCK_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'STOCK_CLOCK_GLOBAL_INVALID');end if;
end;
/
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-15-stock-operation-clock','Prospective UTC native APPLIED observation in stock transaction, no historical backfill',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
