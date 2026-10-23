whenever sqlerror exit failure rollback
declare n number;begin select count(*)into n from RRL_TRADE_ORDER_COMPOSITION where json_value(PAYLOAD_JSON,'$.retry_of' returning number) is not null;if n>0 then raise_application_error(-20999,'COMPOSITION_RETRY_HISTORY_EXISTS');end if;end;
/
@@verify.sql
@@before_body.sql
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-23-trade-composition-retry';
commit;
