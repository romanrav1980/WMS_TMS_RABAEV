declare n number;begin select count(*)into n from RRL_STORE_LOAD_CUSTODY;if n>0 then raise_application_error(-20863,'STORE_CUSTODY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_store_receipt_cmd.sql
@@000_before_rrl_stock_store_return_tr_cmd.sql
@@000_before_rrl_stock_store_return_cust_cmd.sql
@@000_before_rrl_stock_posting_api.sql
@@000_before_rrl_tt_hu_load_fact_guard.sql
drop trigger RRL_STORE_LOAD_CUSTODY_GUARD;
drop table RRL_STORE_LOAD_CUSTODY;
drop package RRL_STOCK_STORE_CUSTODY_CMD;
