create or replace package RRL_CASE_REPORT_SCOPE authid definer as
 procedure begin_change(p_task number,p_actor varchar2);
end;
/
