prompt [migration 2026-05-17-020] Raw material admin settings - rollback

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'RAW_MATERIAL_VIEW',
     'RAW_MATERIAL_EDIT',
     'RAW_MATERIAL_STOCK_VIEW',
     'RAW_MATERIAL_EXPORT'
   );

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-020-raw-material-admin';

commit;

prompt [migration 2026-05-17-020] rollback done
prompt RRL_RAW_MATERIAL_SKU is intentionally preserved; drop it only after explicit operator approval.
