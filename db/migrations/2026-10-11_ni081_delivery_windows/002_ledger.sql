merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-287-delivery-windows-source-v5'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing ST delivery windows and destination norms sourceV5',sysdate,user,'db/migrations/2026-10-11_ni081_delivery_windows/001_body.sql','db/migrations/2026-10-11_ni081_delivery_windows/rollback.sql','APPLIED','Bound200 originalwindows/addressunique-norm-strict-geo; currenthash changes/ownrollbackrestore. Earliestreadonly estimate/HTTPunknown no driver/physicalclaim; SQL4.093ms/2.65ms boundedkeys retained.');
commit;
