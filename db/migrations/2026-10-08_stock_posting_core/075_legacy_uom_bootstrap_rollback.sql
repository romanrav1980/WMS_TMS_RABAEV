declare n number;begin
 select count(*) into n from RRL_STOCK_OPERATION;
 if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_UOM_ROLLBACK');end if;
 delete from RRL_STOCK_UOM_CONVERSION where PROVENANCE='LEGACY_EXPLICIT_UNIT_ZERO_STOCK_20261008';
 delete from RRL_SKU_RECEIPT_POLICY where UPDATED_BY='STOCK_BOOTSTRAP' and POLICY_VERSION=1;
 delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-08-031-explicit-legacy-uom';
end;
/
commit;
