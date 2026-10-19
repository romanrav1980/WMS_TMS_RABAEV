whenever sqlerror exit failure rollback
@@before_api.sql
declare n number;begin
 select count(*)into n from user_errors where name='RRL_TRADE_DOCUMENT_API';
 if n<>0 then raise_application_error(-20999,'TRADECASE_COMPILE_ERRORS');end if;
end;
/
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-document-journal';
commit;
