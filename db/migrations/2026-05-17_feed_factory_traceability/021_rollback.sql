prompt [migration 2026-05-17-021] Finished goods admin settings - rollback

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'FINISHED_GOODS_VIEW',
     'FINISHED_GOODS_EDIT',
     'FINISHED_GOODS_STOCK_VIEW',
     'FINISHED_GOODS_BATCH_VIEW',
     'FINISHED_GOODS_EXPORT'
   );

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-021-finished-goods-admin';

commit;

prompt [migration 2026-05-17-021] rollback done
prompt RRL_FINISHED_GOODS_SKU is intentionally preserved; drop it only after explicit operator approval.
