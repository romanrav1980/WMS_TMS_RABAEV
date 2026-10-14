create or replace package RRL_INTERWARE_UNIT_SOURCE authid definer as
 procedure assert_scope(p_load varchar2,p_actor varchar2);
 procedure capture_plan(p_plan varchar2,p_actor varchar2);
 function plan_manifest(p_plan varchar2,p_actor varchar2)return clob;
 function issued_manifest(p_load varchar2,p_uid varchar2,p_snapshot clob)return clob;
end;

/
