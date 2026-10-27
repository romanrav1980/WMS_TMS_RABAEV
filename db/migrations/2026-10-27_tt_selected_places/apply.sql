whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_journal_table.sql
@@002_writer.sql
@@003_removal_spec.sql
@@004_removal_body.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-tt-selected-places' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Remove selected places of one assembly from a trip through the single membership writer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
