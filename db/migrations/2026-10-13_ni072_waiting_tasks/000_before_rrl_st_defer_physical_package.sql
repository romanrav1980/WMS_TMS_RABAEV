create or replace package RRL_ST_DEFER_PHYSICAL authid definer accessible by(package RRL_ST_DEFER_API)as
 function snapshot(p_st varchar2,p_ware number)return clob;
end;
/
