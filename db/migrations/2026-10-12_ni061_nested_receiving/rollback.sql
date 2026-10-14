declare n number;begin
 select count(*)into n from RRL_INTERWARE_PLAN where SOURCE_HU_JSON is not null;
 if n!=0 then raise_application_error(-20899,'NESTED_PLAN_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;
end;
/
@@000_before_rrl_stock_interware_rec.sql
@@000_before_rrl_interware_plan_guard.sql
@@000_before_rrl_hu_container_guard.sql
@@000_before_rrl_hu_link_write_guard.sql
@@000_before_rrl_hu_departure_guard.sql
drop package RRL_IW_HU_REC_CORE;
drop package RRL_IW_HU_SOURCE;
@@009_recompile.sql
