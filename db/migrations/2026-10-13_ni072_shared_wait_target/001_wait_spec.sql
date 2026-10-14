create or replace package RRL_ST_DEFER_HU_WAIT authid definer
 accessible by(package RRL_ST_DEFER_PHYSICAL,package RRL_ST_DEFER_WAIT_API,package RRL_STOCK_HU_TASK,package RRL_ST_DEFER_PLACE_READ,package RRL_STOCK_HU_CMD)as
 function shared_wait_target(p_request clob,p_task number,p_target varchar2,p_ware number)return boolean;
 function snapshot_root(p_st varchar2,p_ware number,p_root varchar2,p_ignore_plan varchar2 default null)return clob;
 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob;
 procedure request_plan(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_request out clob,p_root varchar2 default null);
 procedure declare_plan(p_request clob,p_task number,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_plan(p_request clob,p_actor varchar2,p_frozen json_object_t,p_task number default null);
end;


/
