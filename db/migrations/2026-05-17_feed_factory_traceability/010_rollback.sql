-- 2026-05-17-010-article-code-length-40 rollback
--
-- The apply script widens article/material code columns from legacy 15/25 to 40.
-- A safe automated rollback must not shrink these columns, because new SAP/S4-length
-- material codes could already exist after the migration.
--
-- If a real rollback is required, first prove there are no values longer than the
-- old limits, take a database snapshot/backup, and then prepare an explicit manual
-- shrink script for the exact target environment.

update RRL_SCHEMA_MIGRATIONS
   set STATUS = 'ROLLBACK_MANUAL_REQUIRED',
       DESCRIPTION = DESCRIPTION || ' | rollback requires manual shrink validation'
 where MIGRATION_ID = '2026-05-17-010-article-code-length-40';

commit;
