whenever sqlerror exit failure rollback
declare n number;begin select count(*)into n from RRL_TRADE_TRIP_LINK;if n>0 then raise_application_error(-20999,'TRADE_TRANSPORT_HISTORY_RETAINED');end if;end;
/
@@before_rrl_stock_trip_depart_cmd.sql
@@before_rrl_stock_unload_cmd.sql
@@before_rrl_stock_loading_read.sql
@@before_rrl_full_shipping_scope.sql
@@before_rrl_trade_stock_guard.sql
@@before_stock_api.sql
drop trigger RRL_TRADE_TRIP_DOC_G;
drop trigger RRL_TRADE_TRIP_LINK_G;
drop table RRL_TRADE_TRIP_DOC_EVENT;
drop table RRL_TRADE_TRIP_LINK;
drop package RRL_TRADE_TRANSPORT_CORE;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-transport-documents';
commit;
