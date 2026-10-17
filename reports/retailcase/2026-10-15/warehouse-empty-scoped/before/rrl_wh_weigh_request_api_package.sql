create or replace package RRL_WH_WEIGH_REQUEST_API authid definer as
 procedure request_capture(p_source clob,p_actor varchar2,p_result out clob);
 procedure request_status(p_request varchar2,p_actor varchar2,p_result out clob);
 procedure assert_device_available(p_device varchar2);
 procedure devices(p_task number,p_purpose varchar2,p_actor varchar2,p_result out clob);
 procedure pending_requests(p_device varchar2,p_actor varchar2,p_result out clob);
 procedure claim_request(p_request varchar2,p_source clob,p_actor varchar2,p_result out clob);
 procedure confirm_zero(p_request varchar2,p_source clob,p_actor varchar2,p_result out clob);
 procedure before_capture(p_source clob,p_actor varchar2);
 procedure validate_first_capture(p_source clob,p_actor varchar2);
 procedure assert_archived_sender(p_source clob,p_actor varchar2);
 procedure validate_archived(p_source clob,p_actor varchar2);
 procedure clear_capture_context;
 function writing(p_id varchar2,p_kind varchar2) return number;
end;
/
