create or replace package RRL_WORKLOAD_CONFIG_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_body clob,p_result out clob);
end;

/
