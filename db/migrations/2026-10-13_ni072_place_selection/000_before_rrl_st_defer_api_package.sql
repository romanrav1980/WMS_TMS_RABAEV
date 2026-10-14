create or replace package RRL_ST_DEFER_API authid definer as
 function write_allowed return number;
 procedure history(p_st varchar2,p_actor varchar2,p_after number,p_result out clob);
 procedure context(p_st varchar2,p_actor varchar2,p_result out clob);
 procedure apply_decision(p_operation varchar2,p_actor varchar2,p_body clob,p_result out clob);
end;

/
