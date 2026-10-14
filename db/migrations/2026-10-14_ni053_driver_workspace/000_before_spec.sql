create or replace package RRL_TT_OPERATION_PLAN_API authid definer as
 procedure generate(p_trip number,p_actor varchar2,p_result out clob);
 procedure write_fact(p_operation number,p_actor varchar2,p_body clob,p_result out clob);
end;

/
