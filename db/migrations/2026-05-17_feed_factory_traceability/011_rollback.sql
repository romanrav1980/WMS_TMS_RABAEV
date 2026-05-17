prompt [migration 2026-05-17-011] MES production completion - rollback

drop package RRL_MES_PRODUCTION_API;

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in (
     'MES_PRODUCTION_VIEW',
     'MES_PRODUCTION_EDIT',
     'MES_PRODUCTION_COMPLETE',
     'MES_WMS_BRIDGE_APPLY'
   );

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-011-mes-production-completion';

commit;

prompt [migration 2026-05-17-011] rollback done
