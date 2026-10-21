whenever sqlerror exit failure rollback
-- Rollback requires an empty queue; never discard pending messages or completed resolutions.
declare n number;begin select count(*)into n from RRL_TRADE_DEFERRED;
 if n<>0 then raise_application_error(-20999,'DEFERRED_ROWS_REQUIRE_EXPORT_AND_RECOVERY');end if;end;
/
@@before_spec.sql
@@before_body.sql
drop table RRL_TRADE_DEFERRED;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-21-tradecase-deferred-documents';
commit;
