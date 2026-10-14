create or replace package RRL_ST_DEFER_WAIT_CORE authid definer as
 procedure check_target(p_cell varchar2,p_ware number);
 function members(p_snapshot clob,p_uid varchar2)return clob;
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/
create or replace package RRL_ST_DEFER_WAIT_API authid definer as
 function write_allowed return number;
 procedure plan_waiting(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_result out clob);
end;
/
