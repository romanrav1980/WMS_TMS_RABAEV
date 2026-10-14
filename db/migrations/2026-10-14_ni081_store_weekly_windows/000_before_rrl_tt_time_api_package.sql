create or replace package RRL_TT_TIME_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure context(p_trip number,p_actor varchar2,p_result out clob);
 procedure approve(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;

/
