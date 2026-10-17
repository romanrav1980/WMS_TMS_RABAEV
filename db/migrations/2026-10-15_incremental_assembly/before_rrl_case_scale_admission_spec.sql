create or replace package RRL_CASE_SCALE_ADMISSION authid definer as
 procedure assert_capture(p_request clob,p_previous number);
 procedure claim_capture(p_request clob,p_operation varchar2,p_previous number);
end;
/
