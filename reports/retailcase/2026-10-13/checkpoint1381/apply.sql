-- MIGRATION_ID: 2026-10-14-1381-st-page-keys
-- Additive covering index for bounded ST header lookup. No business rows changed.
create index RRL_ST_PAGE_KEYS_I on RRL_SBORKA_PALLETS(ST_NUMBER,ADDR,WARE_ID,CONDITION,PALLET_UID);
merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-14-1381-st-page-keys' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Covering index for bounded transport ST headers',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;