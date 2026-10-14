merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-274-supply-document-resources'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'SAP supply individual natural and receipt document resources',sysdate,user,
'db/migrations/2026-10-11_ni011_supply_resources/apply.sql','db/migrations/2026-10-11_ni011_supply_resources/rollback.sql','APPLIED',
'RemovedglobalSRX/sharedCFG4/source-message-originalreceipt keys/currentoriginalWARE/discoveryfreshTxretry. Heldsource independent0.032s/cachedconcurrency/originalforeignWAREdenied/actorrestored/qty1raw3/P20H20/nativeVALID. Freshrevision-receipt competition remains independent.');
commit;
