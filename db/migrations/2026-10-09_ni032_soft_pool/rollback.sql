-- Stop matching pool callers first. Retain reservations, immutable operation results and history.
declare n number;begin
 select count(*) into n from RRL_STOCK_RESERVATION where POOL_WARE_ID is not null and STATUS in('ACTIVE','ALLOCATED') and QTY>0;
 if n>0 then raise_application_error(-20808,'SOFT_POOL_IN_USE: release through root commands before code downgrade');end if;
end;
/
@@../2026-10-08_stock_posting_core/251_ni032_soft_pool_posting_rollback.sql
drop package RRL_STOCK_POOL_CMD;
@@../2026-10-08_stock_posting_core/252_ni032_soft_pool_context_rollback.sql
drop package RRL_STOCK_POOL_READ;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-019-soft-demand-pool';
commit;
/
