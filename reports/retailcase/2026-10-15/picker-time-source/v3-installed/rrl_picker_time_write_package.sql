create or replace package RRL_PICKER_TIME_WRITE authid definer accessible by(package RRL_PICKER_TIME_API) as
 procedure apply_transition(p_actor varchar2,p_action varchar2,p_operation varchar2,p_session number,p_ware number,p_resource number,
  p_kind varchar2,p_id number,p_reason nvarchar2,p_at timestamp with time zone,p_state in out RRL_PICKER_TIME_STREAM%rowtype);
end;
/
