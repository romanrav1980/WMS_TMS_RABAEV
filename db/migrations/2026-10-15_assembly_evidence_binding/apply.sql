-- MIGRATION_ID: 2026-10-15-assembly-evidence-binding
alter table RRL_OPC_SCALE_EVIDENCE drop constraint RRL_OPC_EVIDENCE_KIND_CK;
alter table RRL_OPC_SCALE_EVIDENCE add constraint RRL_OPC_EVIDENCE_KIND_CK check(CAPTURE_KIND in('STORE_RECEIPT','WAREHOUSE_PICK','WAREHOUSE_FINAL','WAREHOUSE_ASSEMBLY'));
@@body.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME='RRL_OPC_EVIDENCE_API';
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_EVIDENCE_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_EVIDENCE_INVALID');end if;
end;
/
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-15-assembly-evidence-binding','OPC provenance1.1 continuous assembly with real initial tare reference',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
