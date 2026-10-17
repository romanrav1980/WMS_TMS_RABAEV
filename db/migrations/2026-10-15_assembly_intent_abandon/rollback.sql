-- Quiesce assembly writers. Preserve nonempty intent history.
declare n number;begin select count(*)into n from RRL_ASM_INTENT_ABANDON;if n!=0 then raise_application_error(-20886,'ASM_INTENT_HISTORY_PRESERVE_FORWARD_REPAIR');end if;end;
/
@@before_assembly_body.sql
drop trigger RRL_ASM_INTENT_GUARD;
drop context RRL_ASM_INTENT_CTX;
drop package RRL_ASM_INTENT_API;
drop table RRL_ASM_INTENT_ABANDON;
declare n number;begin select count(*)into n from USER_ERRORS where NAME='RRL_ASSEMBLY_SCALE_API';if n!=0 then raise_application_error(-20886,'ASM_INTENT_ROLLBACK_COMPILE_ERRORS');end if;select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_INTENT_ROLLBACK_INVALID');end if;end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-assembly-intent-abandon';
commit;
