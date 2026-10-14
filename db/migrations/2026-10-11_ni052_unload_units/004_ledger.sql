merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-213-unload-original-units'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Native unload restores exact original issued physical units and owner HARD',sysdate,user,'db/migrations/2026-10-11_ni052_unload_units/apply.sql','db/migrations/2026-10-11_ni052_unload_units/rollback.sql','APPLIED',
'Actual QPB213DF2C8044/7 original units/14 CRPT+EGAIS codes restored/P7H7/original-7/new+7/late rollback/concurrent one winner/replay/currentWARE403/native cleanup0/protected13520/20. Original composition fingerprint and UNIT60 locks; immutable identities/codes; no government ACK.');
commit;
