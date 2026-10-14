declare n number;begin select count(*)into n from RRL_INTERWARE_DECISION;if n>0 then raise_application_error(-20990,'DISPATCH_DECISION_FACTS_EXIST_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_trip_depart_cmd.sql
@@000_before_rrl_stock_interware_rec.sql
@@000_before_rrl_stock_interware_put.sql
@@000_before_rrl_interware_onward_bind_guard.sql
drop trigger RRL_INTERWARE_DECISION_GUARD;
drop package RRL_INTERWARE_DEPART_GATE;
drop package RRL_INTERWARE_ROUTING;
drop table RRL_INTERWARE_DECISION;
drop index RRL_IW_PLAN_TARGET_I;
