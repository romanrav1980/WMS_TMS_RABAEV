create or replace package RRL_INTERWARE_THERMAL authid definer as
 function mode_json(p_plan varchar2)return clob;
 procedure assert_release(p_plan varchar2);
 procedure assert_cell(p_mode clob,p_ware number,p_cell varchar2);
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob);
end;
/
