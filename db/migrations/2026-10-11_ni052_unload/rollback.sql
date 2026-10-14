declare n number;begin select count(*)into n from RRL_TT_UNLOAD_FACT;if n>0 then raise_application_error(-20863,'UNLOAD_ACTUAL_HISTORY_RETAIN_FORWARD_REPAIR');end if;end;
/
@@000_before_root.sql
@@000_before_balance.sql
@@000_before_reserve.sql
@@000_before_fulfillment.sql
@@000_before_load_guard.sql
@@000_before_member_guard.sql
@@000_before_sample_guard.sql
drop package RRL_STOCK_UNLOAD_CMD;
drop table RRL_TT_UNLOAD_FACT;
