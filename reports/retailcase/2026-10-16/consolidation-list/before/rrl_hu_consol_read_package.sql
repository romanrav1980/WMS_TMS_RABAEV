create or replace package RRL_HU_CONSOL_READ authid definer as
 procedure assert_scope(p_actor nvarchar2,p_ware number,p_permission varchar2);
 procedure assert_plan_scope(p_plan varchar2,p_actor nvarchar2,p_permission varchar2);
 function rows_signature(p_uid varchar2)return varchar2;
 function frozen_plan(p_plan varchar2)return clob;
 function plan_json(p_plan varchar2,p_actor nvarchar2)return clob;
 function shipping_admission(p_root varchar2,p_snapshot clob)return clob;
 procedure assert_shipping_current(p_expected clob,p_root varchar2,p_snapshot clob);
end;
/
