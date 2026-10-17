create or replace package RRL_WH_SCALE_API authid definer as
 procedure capture(p_source clob,p_actor varchar2,p_result out clob);
end;

/
