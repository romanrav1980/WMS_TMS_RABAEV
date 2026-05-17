prompt [migration 2026-05-17-012] WMS warehouse settings - rollback

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in ('WAREHOUSE_SETTINGS_VIEW', 'WAREHOUSE_SETTINGS_EDIT');

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-012-wms-warehouse-settings';

commit;

prompt [migration 2026-05-17-012] rollback done
