whenever sqlerror exit failure rollback
declare n number;begin select count(*)into n from RRL_TRADE_DOCUMENT where ENTITY_TYPE='NEED';if n<>0 then raise_application_error(-20999,'NEED_HISTORY_EXISTS_USE_FORWARD_REPAIR');end if;end;
/
alter table RRL_TRADE_DOCUMENT drop constraint RRL_TRADE_DOC_KIND;
alter table RRL_TRADE_DOCUMENT add constraint RRL_TRADE_DOC_KIND check(ENTITY_TYPE in('OWNER','SKU','RECIPIENT','ORDER','TRIP','SUPPLY'));
@@before_documents.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-need';
commit;
