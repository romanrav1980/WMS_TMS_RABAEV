create or replace package RRL_WTASK_ASSIGN_API authid definer as
 procedure verify_binding;
 function policy_allowed(p_task number,p_action varchar2,p_actor varchar2,p_target varchar2)return number;
 function ledger_write_allowed return number;
 procedure task_context(p_task number,p_actor varchar2,p_target varchar2,p_result out clob);
 procedure execute_command(p_task number,p_request clob,p_actor varchar2,p_result out clob);
 procedure receipt(p_operation varchar2,p_actor varchar2,p_result out clob);
end;
/
