declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='STORE_RECEIPT'and STATE='APPLIED'and json_exists(RESOLVED_PLAN_JSON,'$.domain.marked_unit_proof');if n>0 then raise_application_error(-20863,'MARKED_STORE_RECEIPT_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_store_receipt_cmd.sql
@@000_before_rrl_stock_store_receipt_read.sql
@@000_before_rrl_stock_posting_api.sql
@@005_recompile.sql
