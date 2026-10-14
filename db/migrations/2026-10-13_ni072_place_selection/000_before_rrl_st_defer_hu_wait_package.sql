create or replace package RRL_ST_DEFER_HU_WAIT authid definer
 accessible by(package RRL_ST_DEFER_PHYSICAL,package RRL_ST_DEFER_WAIT_API,package RRL_STOCK_HU_TASK)as
 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob;
 procedure request_plan(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_request out clob);
 procedure declare_plan(p_request clob,p_task number,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_plan(p_request clob,p_actor varchar2,p_frozen json_object_t,p_task number default null);
end;

/
