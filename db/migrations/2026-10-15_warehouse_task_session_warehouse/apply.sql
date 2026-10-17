-- MIGRATION_ID: 2026-10-15-warehouse-task-session-warehouse
@@before.sql
@@body.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-warehouse-task-session-warehouse'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Ordinary native task metadata requires one actual physical warehouse and coherent resource/shift',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
