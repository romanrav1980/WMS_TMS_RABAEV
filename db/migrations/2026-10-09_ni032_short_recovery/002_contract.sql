-- Recovery is metadata around existing stock commands, never a second quantity executor.
create or replace package RRL_STOCK_SHORT_RECOVERY authid definer
 accessible by(package RRL_STOCK_CASE_SHORT_CMD,package RRL_STOCK_INVENTORY_CMD,
 package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_DOMAIN,package RRL_STOCK_CASE_PICK_CMD) as
 procedure plan_inventory(p_request clob,p_resources in out nocopy json_array_t,p_policies in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure finish_inventory(p_request clob,p_actor varchar2,p_domain json_object_t,p_facts json_array_t,p_result in out nocopy json_object_t);
 procedure plan_replenishment(p_repl number,p_resources in out nocopy json_array_t);
 procedure finish_replenishment(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2);
 procedure plan_ready(p_request clob,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure execute_ready(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_pick(p_line number,p_resources in out nocopy json_array_t);
 procedure finish_pick(p_line number,p_actor varchar2);
end;
/
