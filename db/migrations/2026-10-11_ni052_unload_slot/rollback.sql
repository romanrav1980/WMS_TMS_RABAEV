declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='UNLOAD_SHIPMENT'and STATE='APPLIED'and json_exists(RESOLVED_PLAN_JSON,'$.domain.placement_task');if n>0 then raise_application_error(-20863,'UNLOAD_PLACEMENT_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_unload.sql
@@000_before_rrl_hu_task_plan_guard.sql
@@000_before_rrl_hu_claim_measure_guard.sql
@@000_before_slot.sql
@@000_before_placement.sql
