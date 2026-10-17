create or replace package RRL_HU_CONSOL_LIST authid definer as
 function can_view(p_plan varchar2,p_actor nvarchar2)return number;
 function page_json(p_actor nvarchar2,p_ware number,p_after varchar2,p_limit number,p_status varchar2)return clob;
end;
/
