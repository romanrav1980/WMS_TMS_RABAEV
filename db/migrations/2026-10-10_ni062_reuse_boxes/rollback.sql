declare n number;begin select count(*)into n from RRL_RETURN_REUSE_PROOF;if n>0 then raise_application_error(-20808,'REUSE_STOCK_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/420_before107_return_receive.sql
@@../2026-10-08_stock_posting_core/421_before107_return_put.sql
