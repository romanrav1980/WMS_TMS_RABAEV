create or replace package RRL_CASE_ASSIGNMENT_API authid definer as
 function write_allowed(p_task number,p_actor nvarchar2,p_action varchar2)return number;
 function ledger_write_allowed return number;
 procedure execute_command(p_task number,p_request clob,p_actor nvarchar2,p_result out clob);
 procedure task_context(p_task number,p_actor nvarchar2,p_result out clob);
 procedure receipt(p_operation varchar2,p_actor nvarchar2,p_result out clob);
end;
/
create context RRL_CASE_ASSIGNMENT_CTX using RRL_CASE_ASSIGNMENT_API;
