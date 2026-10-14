declare n number;begin select count(*)into n from RRL_STORE_RECEIPT_UNIT;if n>0 then raise_application_error(-20863,'MARKED_UNIT_DISPOSITION_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_store_mark_core.sql
@@000_before_rrl_stock_store_receipt_cmd.sql
@@000_before_rrl_stock_store_receipt_read.sql
@@006_recompile.sql
drop trigger RRL_STORE_RECEIPT_UNIT_GUARD;
drop table RRL_STORE_RECEIPT_UNIT;
alter table RRL_WMS_RECEIPT_UNIT drop constraint RRL_RECEIPT_UNIT_KEY_UK keep index;
