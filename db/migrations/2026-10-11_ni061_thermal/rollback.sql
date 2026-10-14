declare n number;begin select count(*)into n from RRL_INTERWARE_THERMAL_FACT;if n>0 then raise_application_error(-20990,'THERMAL_DECISION_FACTS_EXIST_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_interware_put.sql
@@000_before_rrl_interware_depart_gate.sql
drop trigger RRL_IW_THERMAL_GUARD;
alter table RRL_INTERWARE_PUT_PLAN drop(TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX);
drop package RRL_INTERWARE_THERMAL;
drop table RRL_INTERWARE_THERMAL_FACT;
@@006_recompile.sql
