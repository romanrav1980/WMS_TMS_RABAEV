-- PREPARED only. Root applies after fresh known source/journal baseline review.
@@before.sql
@@spec.sql
@@body.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-case-scoped-close'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Current assigned ordinary CASE metadata close; existing event journal; no stock effects',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
