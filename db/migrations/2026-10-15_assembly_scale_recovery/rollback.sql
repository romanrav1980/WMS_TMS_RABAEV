-- Preserve any real recovery evidence/history: use forward repair after first use.
declare n number;begin
 select(select count(*)from RRL_ASM_RECONCILIATION)+(select count(*)from RRL_ASM_RECON_CAPTURE)into n from dual;
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_RECOVERY_PRESERVE_NONEMPTY_HISTORY');end if;
end;
/
@@before_assembly_spec.sql
@@before_assembly_body.sql
drop context RRL_ASM_RECOVERY_CTX;
drop package RRL_ASSEMBLY_RECOVERY_API;
drop table RRL_ASM_RECON_CAPTURE;
drop table RRL_ASM_RECONCILIATION;
alter table RRL_ASSEMBLY_STEP drop constraint RRL_ASM_STEP_STATE_CK;
alter table RRL_ASSEMBLY_STEP add constraint RRL_ASM_STEP_STATE_CK check(STATE in('WAITING_BEFORE','ARMED','READY','APPLIED','DISCREPANCY'));
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-assembly-scale-recovery';
commit;
