declare n number;begin select count(*)into n from RRL_TARE_OFFER_CANCEL;if n>0 then raise_application_error(-20863,'TARE_CANCEL_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_posting_api.sql
@@000_before_rrl_stock_tare_cmd.sql
@@000_before_rrl_stock_tare_handover.sql
@@000_before_rrl_stock_unload_cmd.sql
drop package RRL_STOCK_TARE_CANCEL_CMD;
drop table RRL_TARE_OFFER_CANCEL;
