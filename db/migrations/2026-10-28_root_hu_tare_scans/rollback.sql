whenever sqlerror exit failure rollback
@@900_before_tare_book_cmd.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-28-root-hu-tare-scans' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Require current root scan/version metadata when booking a container tare',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
