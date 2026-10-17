declare n number;begin
 select count(*)into n from RRL_STORE_RECEIPT_POLICY where RECEIPT_MODE='PAPER_COUNT';
 if n>0 then raise_application_error(-20886,'ROLLBACK_PAPER_STRATEGY_STILL_CONFIGURED');end if;
end;
/
@@before_rrl_stock_store_receipt_read.sql
@@before_rrl_stock_store_receipt_cmd.sql
@@before_rrl_stock_store_weight_core.sql
alter table RRL_STORE_RECEIPT_POLICY drop constraint RRL_STORE_RECEIPT_MODE_CK;
alter table RRL_STORE_RECEIPT_POLICY add constraint RRL_STORE_RECEIPT_MODE_CK check(RECEIPT_MODE in('BARCODE','WEIGHT_PHOTO'));
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-store-app-strategies';
commit;
