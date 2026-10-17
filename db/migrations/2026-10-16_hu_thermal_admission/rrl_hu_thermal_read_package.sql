create or replace package RRL_HU_THERMAL_READ authid definer as
 function admission_json(p_nodes clob,p_ware number,p_cell varchar2,p_more_nodes clob default null)return clob;
 procedure assert_admission(p_admission clob,p_require_known number default 0);
 procedure assert_current(p_expected clob,p_nodes clob,p_ware number,p_cell varchar2,p_more_nodes clob default null);
end;
/
