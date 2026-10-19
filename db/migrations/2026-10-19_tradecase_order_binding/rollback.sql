whenever sqlerror exit failure rollback
declare n number;begin
 select count(*)into n from RRL_TRADE_ORDER_LINK;
 if n>0 then raise_application_error(-20999,'TRADE_ORDER_ROLLBACK_REFUSED_BINDINGS');end if;
end;
/
@@before_rrl_picking_api.sql
@@before_rrl_trade_stock_guard.sql
@@before_rrl_trade_document_api.sql
drop package RRL_TRADE_PICK_CONTEXT;
drop table RRL_TRADE_ORDER_LINE;
drop table RRL_TRADE_ORDER_LINK;
drop table RRL_TRADE_ORDER_COMMAND;
drop package RRL_TRADE_ORDER_API;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-order-binding';
commit;
