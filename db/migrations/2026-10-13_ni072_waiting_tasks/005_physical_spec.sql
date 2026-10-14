create or replace package RRL_ST_DEFER_PHYSICAL authid definer accessible by(package RRL_ST_DEFER_API,package RRL_ST_DEFER_WAIT_API,package RRL_ST_DEFER_WAIT_CORE)as
 function snapshot(p_st varchar2,p_ware number,p_ignore_plan varchar2 default null)return clob;
end;
/
