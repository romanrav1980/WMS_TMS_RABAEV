@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'ASM_ORDER_WRONG_TARGET');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'ASM_ORDER_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_ORDER_INVALID');end if;
end;
/
@@restore_rrl_assembly_scale_api.sql
@@restore_rrl_asm_meta_scope.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'ASM_ORDER_WRONG_TARGET');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'ASM_ORDER_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_ORDER_INVALID');end if;
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-assembly-metadata-lock-order';
commit;
