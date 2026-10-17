create or replace package RRL_CASE_TRANSFER_SCOPE authid definer as
 procedure assert_manager(p_task number,p_actor varchar2);
 procedure assert_target(p_task number,p_target varchar2);
 procedure begin_change(p_task number,p_actor varchar2);
end;
/
