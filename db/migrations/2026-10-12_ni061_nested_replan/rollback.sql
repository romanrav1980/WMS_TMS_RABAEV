declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where STATE='APPLIED'and COMMAND_TYPE='INTERWARE_PUTAWAY_PLAN'and json_exists(RESOLVED_PLAN_JSON,'$.domain.physical_place_uid')and json_exists(RESOLVED_PLAN_JSON,'$.domain.superseded_task_id');if n>0 then raise_application_error(-20899,'RETAINED_HU_TASK_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before.sql
