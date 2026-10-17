create or replace package RRL_IW_GROUP_THERMAL authid definer as
 procedure assert_cell(p_ware number,p_article varchar2,p_cell varchar2);
end;
/
