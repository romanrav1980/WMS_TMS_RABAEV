whenever sqlerror exit failure rollback
declare n number;begin select count(*)into n from RRL_TRADE_CASE_RETURN_UNIT;if n<>0 then raise_application_error(-20999,'TRADE_CASE_RETURN_HISTORY_EXISTS_FORWARD_REPAIR');end if;end;
/
@@before_return.sql
@@before_case_access.sql
@@before_trade_access.sql
@@before_guard.sql
drop package RRL_TRADE_CASE_RETURN;
drop table RRL_TRADE_CASE_RETURN_UNIT;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-case-return';
commit;
