-- MIGRATION_ID: 2026-10-15-assembly-final-snapshot
@@before.sql
@@helper.sql
@@queue_body.sql
@@wh_body.sql
@@assembly_body.sql
@@admission_body.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-15-assembly-final-snapshot','Dedicated ASM_FINAL snapshot v3; shipping admission unchanged except explicit ASM domain rejection',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
