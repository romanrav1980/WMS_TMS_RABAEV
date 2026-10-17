create or replace package RRL_PICKER_TIME_API authid definer as
 procedure verify_binding;
 function write_allowed(p_operator varchar2)return number;
 procedure current_state(p_actor varchar2,p_result out clob);
 procedure execute_command(p_actor varchar2,p_request clob,p_result out clob);
 procedure receipt(p_actor varchar2,p_operation varchar2,p_result out clob);
 procedure read_window(p_actor varchar2,p_start varchar2,p_finish varchar2,p_result out clob);
end;
/
create context RRL_PICKER_TIME_CTX using RRL_PICKER_TIME_API;
