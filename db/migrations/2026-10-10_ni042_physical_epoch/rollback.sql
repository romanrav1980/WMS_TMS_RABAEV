-- Keep additive history columns; disable only this guard before restoring the previous balance source.
declare n number;begin
 select count(*) into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID in('2026-10-10-073-stock-composition-epoch','2026-10-10-074-stock-leaf-placement') and STATUS='APPLIED';
 if n>0 then raise_application_error(-20886,'DEPENDENT_STOCK_PLACEMENT_REQUIRES_PHYSICAL_EPOCH');end if;
 select count(*) into n from RRL_RECEIPT_SLOT_CLAIM where HU_PHYSICAL_VERSION is not null;
 if n>0 then raise_application_error(-20886,'MEASURED_STOCK_CLAIMS_REQUIRE_PHYSICAL_EPOCH');end if;
end;
/
drop trigger RRL_PHYSICAL_VERSION_GUARD;
@@../2026-10-08_stock_posting_core/357_checkpoint_physical_epoch_balance.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-072-physical-stock-epoch';
commit;
/
