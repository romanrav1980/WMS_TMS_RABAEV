create or replace package RRL_TT_ROUTE_SCHEDULE as
 procedure material(p_source clob,p_result out clob);
 procedure lock_material(p_source clob);
 procedure calculate(p_source clob,p_zone varchar2,p_result out clob);
 procedure assert_chain(p_segments clob,p_zone varchar2);
end;

/
