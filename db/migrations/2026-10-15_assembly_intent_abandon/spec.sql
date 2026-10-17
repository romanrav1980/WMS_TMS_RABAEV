create or replace package RRL_ASM_INTENT_API authid definer as
 function write_allowed return number;
 procedure assert_available(p_kind varchar2,p_actor nvarchar2,p_task number,p_session varchar2,p_step varchar2 default null,p_operation varchar2 default null);
 procedure abandon(p_request clob,p_actor nvarchar2,p_result out clob);
 procedure describe(p_id varchar2,p_actor nvarchar2,p_result out clob);
end;
/
create context RRL_ASM_INTENT_CTX using RRL_ASM_INTENT_API;
