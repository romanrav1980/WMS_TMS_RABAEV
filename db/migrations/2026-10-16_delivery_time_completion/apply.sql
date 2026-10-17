@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-16-delivery-time','Immutable delivery window and arrival; completion after inaccessible ALL_CONTEXT owner read; native owner probe verified',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
