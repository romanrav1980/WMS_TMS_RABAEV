merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-298-final-lineage-source-index'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Bounded final receipt source-load lookup',sysdate,user,'db/migrations/2026-10-11_ni053_lineage_lookup/001_index.sql','db/migrations/2026-10-11_ni053_lineage_lookup/rollback.sql','APPLIED','SourceLoad OPID indexVALID, native stats; scoped NL exactsame full andpartialprojections. Avg70.349ms6278buffers to20.529ms146buffers total3; no stock/historychanges.');
commit;
