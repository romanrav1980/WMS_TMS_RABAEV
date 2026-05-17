-- 2026-05-17-009-bom-production-block rollback
--
-- Safe rollback: keep BOM tables and historical recipe data.
-- This script removes only the PL/SQL package and migration ledger row.

drop package RRL_BOM_API;

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-17-009-bom-production-block';

commit;
