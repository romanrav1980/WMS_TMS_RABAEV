@@001_schema.sql
@@002_helper.sql
@@003_tare_command.sql
@@004_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_TARE_HANDOVER','RRL_STOCK_TARE_CMD','RRL_TARE_BOOK_GUARD','RRL_TARE_OFFER_BOOK_GUARD') and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'TARE_BOOKED_HANDOVER_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-102-booked-tare-driver-handover' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Selected same-counter assembly tare binds existing physical load root; actual driver acceptance atomically transfers book and quantity, no nested count/second goods posting',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
