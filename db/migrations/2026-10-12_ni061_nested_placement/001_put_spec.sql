create or replace package RRL_STOCK_INTERWARE_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN,package RRL_STOCK_HU_TASK) as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2,p_superseded number default null);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;

/
