whenever sqlerror exit failure rollback
@@before_assignment.sql
@@before_case_access.sql
@@before_trade_spec.sql
@@before_trade_body.sql
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin select count(*)into n from user_objects where STATUS='INVALID'and OBJECT_NAME not like'BIN$%';if n<>0 then raise_application_error(-20999,'TRADE_MARKED_CASE_INVALID_OBJECTS');end if;end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-marked-case-scope';
commit;
