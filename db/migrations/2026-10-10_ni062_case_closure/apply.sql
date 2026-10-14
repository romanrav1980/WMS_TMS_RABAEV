@@001_schema.sql
@@002_helper.sql
@@003_command.sql
@@004_case_guard.sql
@@005_fact_guard.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-117-investigated-case-explicit-closure' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Ordinary discrepancy closure through original versioned case root/two findings/independent KRO/no unresolved quantities/immutable evidence/SAP pending/no second stock',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
