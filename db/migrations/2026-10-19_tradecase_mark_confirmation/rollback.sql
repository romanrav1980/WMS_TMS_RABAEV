whenever sqlerror exit failure rollback
declare n number;begin
 select count(*)into n from RRL_TRADE_MARK_EVENT;
 if n>0 then raise_application_error(-20999,'TRADE_MARK_ROLLBACK_REFUSED_EVENTS');end if;
end;
/
@@before_api.sql
drop table RRL_TRADE_MARK_EVENT;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-mark-confirmation';
commit;
