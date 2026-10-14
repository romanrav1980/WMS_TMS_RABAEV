@@001_schema.sql
@@002_reader.sql
@@003_policy.sql
@@004_gate.sql
@@005_shipping.sql
@@006_quality.sql
@@007_exemption_lookup.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-1447-ni051-scoped-quality' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Scoped QC rules, versioned current policy and immutable whole-pallet exemption under original stock root',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
