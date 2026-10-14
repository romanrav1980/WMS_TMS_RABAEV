declare n number;begin select count(*)into n from RRL_WH_SCALE_USE;if n>0 then raise_application_error(-20863,'WAREHOUSE_SCALE_USE_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_case.sql
drop trigger RRL_WH_SCALE_USE_GUARD;
drop package RRL_CASE_SCALE_ADMISSION;
drop table RRL_WH_SCALE_USE;
