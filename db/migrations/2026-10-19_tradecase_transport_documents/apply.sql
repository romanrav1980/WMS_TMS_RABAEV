whenever sqlerror exit failure rollback
@@001_schema.sql
@@002_core.sql
@@003_stock_api.sql
@@004_write_guards.sql
@@005_stock_guard.sql
@@006_shipping_scope.sql
@@007_loading_read.sql
@@008_unload.sql
@@009_depart.sql
declare n number;begin
 select count(*)into n from user_errors where NAME in('RRL_TRADE_TRANSPORT_CORE','RRL_TRADE_STOCK_API','RRL_TRADE_TRIP_LINK_G','RRL_TRADE_TRIP_DOC_G','RRL_TRADE_STOCK_GUARD','RRL_FULL_SHIPPING_SCOPE','RRL_STOCK_LOADING_READ','RRL_STOCK_UNLOAD_CMD','RRL_STOCK_TRIP_DEPART_CMD');
 if n<>0 then raise_application_error(-20999,'TRADE_TRANSPORT_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-transport-documents'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Bind external trip and durable business transport document readiness to current physical manifest',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
