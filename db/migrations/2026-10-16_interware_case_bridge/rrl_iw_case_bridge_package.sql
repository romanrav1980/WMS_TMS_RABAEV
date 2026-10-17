create or replace package RRL_IW_CASE_BRIDGE authid definer as
 function source_cases(p_load varchar2,p_tree clob)return clob;
 function origin_json(p_uid varchar2)return clob;
 function historical_member(p_uid varchar2)return number;
 procedure assert_container(p_uid varchar2,p_type varchar2,p_cell varchar2,p_tare number,p_identifier varchar2);
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2);
end;
/
