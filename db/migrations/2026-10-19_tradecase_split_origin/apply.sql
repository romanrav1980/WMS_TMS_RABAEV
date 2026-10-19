whenever sqlerror exit failure rollback
@@001_internal.sql
@@002_clone_guard.sql
declare n number;begin
 select count(*)into n from user_errors where NAME in('RRL_STOCK_INTERNAL_CMD','RRL_SAP_PALLET_WRITE_GUARD');
 if n<>0 then raise_application_error(-20999,'TRADE_SPLIT_ORIGIN_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-split-origin'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Retain immutable receipt origin while locking and authorizing the actual physical split source',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
