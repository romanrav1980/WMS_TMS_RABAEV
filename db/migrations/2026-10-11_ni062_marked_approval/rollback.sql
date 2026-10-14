declare n number;begin select count(*)into n from RRL_STORE_RETURN_UNIT;if n>0 then raise_application_error(-20863,'MARKED_RETURN_APPROVAL_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_store_return_cmd.sql
@@000_before_rrl_stock_posting_api.sql
@@006_recompile.sql
drop trigger RRL_STORE_RETURN_UNIT_GUARD;
drop table RRL_STORE_RETURN_UNIT;
drop package RRL_STORE_RETURN_UNIT_CORE;
