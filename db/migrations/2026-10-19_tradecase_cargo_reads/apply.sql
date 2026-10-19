whenever sqlerror exit failure rollback
@@001_stock_read.sql
@@002_transport_read.sql
declare n number;begin select count(*)into n from user_errors where NAME in('RRL_TRADE_STOCK_API','RRL_TRADE_TRANSPORT_CORE');if n<>0 then raise_application_error(-20999,'TRADE_CARGO_READ_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-cargo-reads'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Read CASE label units and exact departed cargo with legal-owner scopes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
