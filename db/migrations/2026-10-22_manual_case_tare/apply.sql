whenever sqlerror exit failure rollback
@@before_guard.sql
@@001_manual_tare.sql
@@002_pick_admission.sql
@@003_final_admission.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-manual-case-tare' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Explicit manual empty tare, native append-only evidence and CASE weight admission',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
