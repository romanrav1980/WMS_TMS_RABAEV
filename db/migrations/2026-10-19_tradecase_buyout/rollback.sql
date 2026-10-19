whenever sqlerror exit failure rollback
declare n number;begin
 select count(*)into n from RRL_TRADE_BUYOUT;
 if n>0 then raise_application_error(-20999,'TRADE_BUYOUT_ROLLBACK_REFUSED_BUSINESS_HISTORY');end if;
 select count(*)into n from RRL_TRADE_DOCUMENT where ENTITY_TYPE='ORDER'and json_value(BODY_JSON,'$.order_kind')='BUYOUT';
 if n>0 then raise_application_error(-20999,'TRADE_BUYOUT_ROLLBACK_REFUSED_FINANCIAL_BASES');end if;
end;
/
@@before_rrl_trade_stock_api.sql
@@before_rrl_trade_stock_guard.sql
@@before_rrl_trade_document_api.sql
@@before_rrl_trade_order_api.sql
drop package RRL_TRADE_BUYOUT_CORE;
drop table RRL_TRADE_BUYOUT_EVENT;
drop table RRL_TRADE_BUYOUT_UNIT;
drop table RRL_TRADE_BUYOUT;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-buyout';
commit;
