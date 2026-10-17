create or replace package RRL_STOCK_LOAD_BOX_CORE authid definer accessible by(package RRL_STOCK_HU_LOAD_CORE) as
 procedure compile_boxes(p_snapshot clob,p_context clob,p_operation varchar2,p_gross number,r in out nocopy json_array_t,p_boxes out json_array_t);
 procedure assert_policy(p_destinations clob,p_boxes json_array_t);
 procedure persist_boxes(p_operation varchar2,p_boxes json_array_t,p_actor varchar2);
end;
/
