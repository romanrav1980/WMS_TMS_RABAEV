-- MIGRATION_ID: 2026-10-15-opc-scale-evidence
@@schema.sql
@@body.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_OPC_EVIDENCE_API','RRL_OPC_EVIDENCE_GUARD');
 if n!=0 then raise_application_error(-20886,'OPC_EVIDENCE_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'OPC_EVIDENCE_GLOBAL_INVALID');end if;
end;
/
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-15-opc-scale-evidence','Immutable gateway-reported OPC provenance; native capture hash binding, no stock effects',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
