-- Quiesce archive writers. Preserve any nonempty reconciliation provenance history.
declare n number;begin
 select count(*)into n from RRL_OPC_SCALE_EVIDENCE where CAPTURE_KIND='WAREHOUSE_ASSEMBLY_RECON';
 if n!=0 then raise_application_error(-20886,'OPC_RECOVERY_EVIDENCE_HISTORY_PRESERVE');end if;
end;
/
@@before_body.sql
alter table RRL_OPC_SCALE_EVIDENCE drop constraint RRL_OPC_EVIDENCE_KIND_CK;
alter table RRL_OPC_SCALE_EVIDENCE add constraint RRL_OPC_EVIDENCE_KIND_CK check(CAPTURE_KIND in('STORE_RECEIPT','WAREHOUSE_PICK','WAREHOUSE_FINAL','WAREHOUSE_ASSEMBLY'));
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-assembly-reconciliation-evidence';
commit;
