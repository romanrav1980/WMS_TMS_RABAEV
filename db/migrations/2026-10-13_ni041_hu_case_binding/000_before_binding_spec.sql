create or replace package RRL_STOCK_CASE_BIND_MOVE authid definer accessible by(package RRL_STOCK_CASE_MOVE_CMD)as

 procedure plan_move(p_case RRL_CASE_PICK_TASK%rowtype,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);

 procedure validate_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t);

 procedure finish_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t,p_version number,p_actor varchar2);

end;


/
