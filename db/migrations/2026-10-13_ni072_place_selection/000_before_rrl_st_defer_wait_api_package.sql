create or replace package RRL_ST_DEFER_WAIT_API authid definer as

 function write_allowed return number;

 procedure plan_waiting(p_operation varchar2,p_decision varchar2,p_actor varchar2,p_result out clob);

 procedure record_hu_plan(p_request clob,p_task number,p_frozen json_object_t,p_result in out clob);
end;



/
