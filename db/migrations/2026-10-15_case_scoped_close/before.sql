@@known_sources_guard.sql
@@journal_baseline_guard.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_CASE_LIFECYCLE_API';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_NAMESPACE_EXISTS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_BEFORE_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_BEFORE_ERRORS');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-case-scoped-close'and STATUS!='ROLLED_BACK';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_ALREADY_APPLIED');end if;
end;
/
