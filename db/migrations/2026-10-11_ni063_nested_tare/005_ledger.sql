merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-176-nested-tare-preservation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Explicit retained CASE tare booking in HU attachment and archive-bound nested handover',sysdate,user,'db/migrations/2026-10-11_ni063_nested_tare/apply.sql','db/migrations/2026-10-11_ni063_nested_tare/rollback.sql','APPLIED','Owned409 original tare books1048/1049 retained through native attach/unpack/slot movement then cancelled only after actual root return; current HU composition/slot read scope admin200 foreign403; full nested outbound handover remains positive acceptance pending');
commit;
