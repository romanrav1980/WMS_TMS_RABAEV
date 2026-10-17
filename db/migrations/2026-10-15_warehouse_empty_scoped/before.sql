@@before_source_guard.sql
@@history_baseline_guard.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'WH_EMPTY_SCHEMA_REQUIRED');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WH_EMPTY_BEFORE_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'WH_EMPTY_BEFORE_ERRORS');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-warehouse-empty-scoped'and STATUS!='ROLLED_BACK';if n!=0 then raise_application_error(-20886,'WH_EMPTY_ALREADY_APPLIED');end if;
end;
/
