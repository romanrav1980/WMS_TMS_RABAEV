create or replace package RRL_CASE_RESOURCE_POLICY authid definer as
 function context_json(p_task number,p_action varchar2,p_actor varchar2,p_resource number default null,p_session number default null,p_equipment number default null) return clob;
end;
/
