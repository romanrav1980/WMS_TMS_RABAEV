create or replace package RRL_RESOURCE_INTENT_API authid definer as
 procedure verify_binding;
 function write_allowed(p_control varchar2,p_domain varchar2,p_original varchar2)return number;
 procedure assert_available(p_domain varchar2,p_task number,p_actor nvarchar2,p_operation varchar2,p_original clob);
 procedure abandon(p_request clob,p_actor nvarchar2,p_result out clob);
 procedure describe(p_control varchar2,p_actor nvarchar2,p_result out clob);
 procedure resolve(p_domain varchar2,p_task number,p_operation varchar2,p_action varchar2,p_target nvarchar2,p_sha varchar2,p_actor nvarchar2,p_result out clob);
end;
/
create context RRL_RESOURCE_INTENT_CTX using RRL_RESOURCE_INTENT_API;
