@@001_schema.sql
@@002_planning.sql
@@003_command.sql
@@004_tare_command.sql
@@005_resolution_command.sql
@@006_root.sql
@@007_balance_guards.sql
@@008_book_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_TARE_PLANNING','RRL_STOCK_TARE_BOOK_CMD','RRL_STOCK_TARE_CMD','RRL_STOCK_TARE_RESOLVE','RRL_STOCK_POSTING_API','RRL_TARE_AVAILABILITY','RRL_TARE_BOOK_GUARD','RRL_CASE_TARE_START_GUARD','RRL_HU_TARE_LINK_GUARD','RRL_HU_TARE_WARE_GUARD') and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_ASSEMBLY_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-101-tare-existing-assembly' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing CASE/HU assembly holds real good warehouse tare; root booking/cancel, guarded start, no nested duplicate/free planned returns; no new picking engine',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
