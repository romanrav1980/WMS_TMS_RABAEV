@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'ASM_ORDER_WRONG_TARGET');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'ASM_ORDER_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_ORDER_INVALID');end if;
end;
/
@@rrl_asm_meta_scope.sql
@@rrl_assembly_scale_api.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-16-assembly-metadata-lock-order','ASM begin_plan before TX/REV; owned cleanup and unchanged legacy permission',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
