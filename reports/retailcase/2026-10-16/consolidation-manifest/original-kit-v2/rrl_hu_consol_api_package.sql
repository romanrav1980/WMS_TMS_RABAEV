create or replace package RRL_HU_CONSOL_API authid definer as
 procedure execute_command(p_actor nvarchar2,p_command clob,p_result out clob);
 procedure assert_write(p_plan varchar2,p_operation varchar2 default null);
end;
/
