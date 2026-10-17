-- MIGRATION_ID: 2026-10-15-assembly-intent-abandon
-- Partial initial DDL retained; fix private function SQL boundary, no new objects.
@@body.sql
alter package RRL_ASSEMBLY_SCALE_API compile body;
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-15-assembly-intent-abandon','Fenced explicit abandonment of proven absent assembly open intents',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
