whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_function.sql
@@002_pick_context_body.sql
@@003_transport_core_body.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-trade-recipient-version' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Pick context and trip demand accept a later recipient version differing only in top-up settings',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
