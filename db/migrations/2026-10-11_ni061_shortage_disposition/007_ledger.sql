merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-295-interware-shortage-disposition'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Independent carrier shortage report and confirmation via existing stock root',sysdate,user,'db/migrations/2026-10-11_ni061_shortage_disposition/001_schema.sql','db/migrations/2026-10-11_ni061_shortage_disposition/rollback.sql','APPLIED','Actual ordinary and marked partial short2 independently confirmed; rollback/race/replay/collision, acceptedP1/source0. No repeated stock deduction/custody release/GovACK. Missing-unit book blocks ordinary mutation pending correction.');
commit;
