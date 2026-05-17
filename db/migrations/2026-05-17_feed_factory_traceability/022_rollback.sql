prompt [migration 2026-05-17-022] Slow SQL diagnostics - rollback

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) = 'SLOW_SQL_VIEW';

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-022-slow-sql-diagnostics';

commit;

prompt [migration 2026-05-17-022] rollback done
prompt RRL_SQL_SLOW_LOG is intentionally preserved; drop it only after explicit operator approval.
