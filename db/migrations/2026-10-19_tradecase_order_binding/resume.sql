whenever sqlerror exit failure rollback
@@002_api.sql
@@003_context.sql
@@004_stock_guard.sql
@@005_picking_hook.sql
@@006_guards.sql
@@007_document_api.sql
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_ORDER_API','RRL_TRADE_PICK_CONTEXT','RRL_TRADE_STOCK_GUARD','RRL_PICKING_API','RRL_TRADE_DOCUMENT_API','RRL_TRADE_ORDER_LINK_G','RRL_TRADE_ORDER_LINE_G','RRL_TRADE_ORDER_CMD_G');
 if n<>0 then raise_application_error(-20999,'TRADE_ORDER_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-order-binding'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Legal order binding and native planner context; no duplicate quantity ledger',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
