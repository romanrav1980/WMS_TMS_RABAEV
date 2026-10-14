declare n number;begin select count(*)into n from RRL_INTERWARE_PLAN where nvl(json_value(SOURCE_COMPOSITION_JSON,'$.physical_unit_count' returning number),0)>0;if n>0 then raise_application_error(-20863,'MARKED_INTERWARE_PLAN_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_interware_plan_guard.sql
drop table RRL_INTERWARE_UNIT_MANIFEST;
drop package RRL_INTERWARE_UNIT_SOURCE;
