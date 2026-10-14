merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-267-erp-source-admission'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Versioned ERP source admission and rejection without rewriting source demand',sysdate,user,
'db/migrations/2026-10-11_ni022_admission/apply.sql','db/migrations/2026-10-11_ni022_admission/rollback.sql','APPLIED',
'Two original264 sources only/atomic rollback/concurrent202-409/immutable exact replay/forged declaredhash refused/current calendar-deadline-planning freeze/raw source retained/no stock/source birth/P20H20/nativeVALID. Local gateway result is not real SAP acknowledgment.');
commit;
