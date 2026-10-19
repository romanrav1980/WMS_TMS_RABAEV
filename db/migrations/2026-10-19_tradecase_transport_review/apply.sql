whenever sqlerror exit failure rollback
@@001_transit_proof.sql
@@002_stock_reads.sql
@@003_buyout.sql
@@004_transport.sql
@@005_stock_guard.sql
@@006_pick_context.sql
@@007_order_bind.sql
declare n number;begin select count(*)into n from user_errors where NAME like'RRL_TRADE%';if n<>0 then raise_application_error(-20999,'TRADE_REVIEW_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-transport-review'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Verify immutable issued unit set, bound pack factors and complete trip membership',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
