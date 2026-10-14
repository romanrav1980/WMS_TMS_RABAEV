drop trigger RRL_DEFER_WAIT_CELL_GUARD;
/
alter table RRL_RECEIPT_WARE_SETTINGS drop column DEFER_WAIT_CELL;
/
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-12-761-defer-wait-cell';
/
