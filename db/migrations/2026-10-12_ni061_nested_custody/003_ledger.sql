merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-318-nested-custody-place' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Custody release uses actual frozen physical top HU independently of stock leaf while preserving original quantity and departure proofs',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
