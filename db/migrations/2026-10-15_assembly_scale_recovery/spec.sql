create or replace package RRL_ASSEMBLY_RECOVERY_API authid definer as
 function write_allowed return number;
 procedure request_reconciliation(p_session varchar2,p_request clob,p_actor nvarchar2,p_result out clob);
 procedure authorize(p_id varchar2,p_request clob,p_actor nvarchar2,p_result out clob);
 procedure read_reconciliation(p_id varchar2,p_actor nvarchar2,p_result out clob);
 procedure gateway_requests(p_device varchar2,p_sender nvarchar2,p_result out clob);
 procedure capture(p_request clob,p_sender nvarchar2,p_result out clob);
 procedure capture_state(p_id varchar2,p_sender nvarchar2,p_result out clob);
 procedure assert_apply(p_id varchar2,p_session varchar2,p_step varchar2);
end;
/
create or replace context RRL_ASM_RECOVERY_CTX using RRL_ASSEMBLY_RECOVERY_API;
