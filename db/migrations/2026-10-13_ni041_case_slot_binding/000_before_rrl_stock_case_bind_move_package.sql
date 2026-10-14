create or replace package RRL_STOCK_CASE_BIND_MOVE authid definer accessible by(package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_HU_CMD)as

 procedure plan_move(p_case RRL_CASE_PICK_TASK%rowtype,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);

 procedure validate_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t);

 procedure finish_move(p_case RRL_CASE_PICK_TASK%rowtype,p_frozen json_object_t,p_version number,p_actor varchar2);

 procedure plan_tree(p_nodes json_array_t,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);

 procedure validate_tree(p_nodes json_array_t,p_domain json_object_t);

 function binding_for(p_domain json_object_t,p_case_id number)return json_object_t;

end;


/
