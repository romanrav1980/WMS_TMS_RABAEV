-- MIGRATION_ID: 2026-10-15-assembly-evidence-shape-fix
@@body.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME='RRL_OPC_EVIDENCE_API';
 if n!=0 then raise_application_error(-20886,'OPC_EVIDENCE_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'OPC_EVIDENCE_GLOBAL_INVALID');end if;
end;
/
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-15-assembly-evidence-shape-fix','Use default JSON mode only for optional shape probes; preserve strict required fields',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
