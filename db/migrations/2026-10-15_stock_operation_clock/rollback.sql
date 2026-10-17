-- Maintenance only: stop all stock writers before the empty-history guard and DDL.
declare n number;begin
 select count(*)into n from RRL_STOCK_OP_CLOCK;
 if n!=0 then raise_application_error(-20886,'STOCK_CLOCK_NONEMPTY_HISTORY_PRESERVE');end if;
end;
/
drop trigger RRL_STOCK_APPLIED_CLOCK;
drop trigger RRL_STOCK_CLOCK_GUARD;
drop table RRL_STOCK_OP_CLOCK;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-stock-operation-clock';
commit;
