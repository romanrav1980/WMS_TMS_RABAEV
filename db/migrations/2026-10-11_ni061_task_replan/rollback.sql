declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='INTERWARE_PUTAWAY_PLAN'and STATE='APPLIED'and json_exists(RESOLVED_PLAN_JSON,'$.domain.superseded_task_id');if n>0 then raise_application_error(-20990,'REPLAN_FACTS_EXIST_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_interware_put.sql
@@000_before_rrl_stock_posting_api.sql
@@003_recompile.sql
