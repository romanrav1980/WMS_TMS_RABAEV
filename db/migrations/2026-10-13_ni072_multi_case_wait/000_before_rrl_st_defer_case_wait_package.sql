create or replace package RRL_ST_DEFER_CASE_WAIT authid definer as

 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob;

 procedure assert_command(p_request clob,p_actor varchar2);

 procedure plan_move(p_request clob,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);

 procedure validate_move(p_request clob,p_actor varchar2,p_frozen json_object_t);

 procedure finish_move(p_request clob,p_actor varchar2,p_result in out clob);

end;


/
