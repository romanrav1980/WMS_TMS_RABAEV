whenever sqlerror exit failure rollback
declare n number;begin
 select sum(amount)into n from(select count(*) amount from RRL_TRADE_STOCK_ATTR union all select count(*) from RRL_TRADE_CELL_POLICY union all select count(*) from RRL_TRADE_OWNER_GRANT union all select count(*) from RRL_TRADE_STOCK_COMMAND);
 if n>0 then raise_application_error(-20999,'TRADE_STOCK_ROLLBACK_REFUSED_BOUND_UNITS');end if;
 select count(*)into n from RRL_TRADE_DOCUMENT where ENTITY_TYPE='SUPPLY';
 if n>0 then raise_application_error(-20999,'TRADE_STOCK_ROLLBACK_REFUSED_SUPPLY_DOCUMENTS');end if;
end;
/
@@before_rrl_stock_posting_api.sql
@@before_rrl_stock_invariant_core.sql
@@before_rrl_stock_eligibility.sql
@@before_rrl_trade_document_api.sql
drop package RRL_TRADE_STOCK_API;
drop package RRL_TRADE_STOCK_GUARD;
drop table RRL_TRADE_STOCK_COMMAND;
drop table RRL_TRADE_OWNER_GRANT;
drop table RRL_TRADE_CELL_POLICY;
drop table RRL_TRADE_STOCK_ATTR;
alter table RRL_TRADE_DOCUMENT drop constraint RRL_TRADE_DOC_KIND;
alter table RRL_TRADE_DOCUMENT add constraint RRL_TRADE_DOC_KIND check(ENTITY_TYPE in('OWNER','SKU','RECIPIENT','ORDER','TRIP'));
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-stock-attributes';
commit;
