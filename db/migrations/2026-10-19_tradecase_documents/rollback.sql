whenever sqlerror exit failure rollback
declare n number;begin
 select count(*)into n from RRL_TRADE_SITE;
 if n<>0 then raise_application_error(-20999,'ROLLBACK_REFUSED_NONEMPTY_TRADECASE');end if;
end;
/
drop package RRL_TRADE_DOCUMENT_API;
drop table RRL_TRADE_MESSAGE;
drop table RRL_TRADE_DOCUMENT;
drop table RRL_TRADE_SITE;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-documents';
commit;