merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-265-current-store-source-scope'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Current warehouse authority and shared configuration-bound SAP source commands',sysdate,user,
'db/migrations/2026-10-11_ni022_source_scope/apply.sql','db/migrations/2026-10-11_ni022_source_scope/rollback.sql','APPLIED',
'Nativeactor-currentWARE/view-import-prepare/currentcache-afterwait/sharedCFG4-RELEASE/resourceHELD-ROW20CO-SAPsource/wait3/no stock-context. Original264two sources reused/HTTP200-foreign403/currentWarehousechange cachedread-import-prepare denied/revoke/actorretired/P20H20. Source wrappers no new splitter.');
commit;
