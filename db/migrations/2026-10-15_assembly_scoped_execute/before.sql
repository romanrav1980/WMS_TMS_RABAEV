@@before_sources.sql
@@history_guard.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'ASM_SCOPE_WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_SCOPE_BEFORE_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'ASM_SCOPE_BEFORE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_ASM_META_SCOPE';if n!=0 then raise_application_error(-20886,'ASM_SCOPE_NAMESPACE');end if;
 select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-assembly-scoped-execute'and STATUS!='ROLLED_BACK';if n!=0 then raise_application_error(-20886,'ASM_SCOPE_ALREADY_APPLIED');end if;
end;
/
