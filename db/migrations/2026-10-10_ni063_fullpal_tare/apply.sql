@@001_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_TARE_BOOK_CMD' and STATUS='INVALID';if n!=0 then raise_application_error(-20808,'FULLPAL_TARE_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-103-standalone-stock-pallet-tare' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Reuse BOOK/actual root loading/handover for standalone STOCK physical pallet, original current single stock cell, no fake container',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
