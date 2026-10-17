create or replace package RRL_ASSEMBLY_SCALE_API authid definer as
 function write_allowed(p_kind varchar2)return number;
 procedure station_policy(p_device varchar2,p_request clob,p_actor nvarchar2,p_result out clob);
 procedure sku_policy(p_request clob,p_actor nvarchar2,p_result out clob);
 procedure open_session(p_request clob,p_actor nvarchar2,p_result out clob);
 procedure open_step(p_session varchar2,p_request clob,p_actor nvarchar2,p_result out clob);
 procedure capture(p_request clob,p_sender nvarchar2,p_result out clob);
 procedure placed(p_step varchar2,p_actor nvarchar2,p_result out clob);
 procedure finish(p_session varchar2,p_request clob,p_actor nvarchar2,p_result out clob);
 procedure context(p_task number,p_actor nvarchar2,p_result out clob);
 procedure read_session(p_session varchar2,p_actor nvarchar2,p_result out clob);
 procedure read_step(p_step varchar2,p_actor nvarchar2,p_result out clob);
 procedure gateway_requests(p_device varchar2,p_sender nvarchar2,p_result out clob);
 procedure posting_request(p_step varchar2,p_caller nvarchar2,p_result out clob);
 procedure assert_post(p_request clob,p_previous number);
 procedure claim_post(p_request clob,p_operation varchar2,p_previous number);
end;
/
