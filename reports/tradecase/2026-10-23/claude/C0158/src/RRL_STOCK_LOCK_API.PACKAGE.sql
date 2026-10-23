package RRL_STOCK_LOCK_API authid definer as
 function resource_lock_id(p_rank number,p_key raw) return number;
 function resource_key(p_kind varchar2,p_a varchar2,p_b varchar2 default null,p_c varchar2 default null) return raw;
 procedure begin_plan;
 procedure acquire_policies(p_plan clob);
 procedure acquire_resources(p_plan clob);
 procedure assert_held(p_rank number,p_key raw);
 procedure assert_policy(p_key raw,p_mode number);
 procedure clear_plan;
end;