whenever sqlerror exit failure rollback
@@001_schema.sql
@@002_core.sql
declare n number;begin
 select count(*)into n from user_errors where name='RRL_TRADE_BUYOUT_CORE';
 if n<>0 then raise_application_error(-20999,'TRADE_BUYOUT_CORE_COMPILE_ERRORS');end if;
end;
/
@@003_stock_api.sql
@@004_stock_guard.sql
@@005_document_api.sql
@@006_order_binding_guard.sql
@@007_write_guards.sql
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_BUYOUT_CORE','RRL_TRADE_STOCK_API','RRL_TRADE_STOCK_GUARD','RRL_TRADE_DOCUMENT_API','RRL_TRADE_ORDER_API','RRL_TRADE_BUYOUT_G','RRL_TRADE_BUYOUT_UNIT_G','RRL_TRADE_BUYOUT_EVENT_G');
 if n<>0 then raise_application_error(-20999,'TRADE_BUYOUT_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-buyout'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Financial basis and per-code ownership transfer with durable SKM outcomes, independent holds and regulatory journal',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
