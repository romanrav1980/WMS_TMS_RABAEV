create or replace package RRL_PICKER_TIME_READ authid definer accessible by(package RRL_PICKER_TIME_API) as
 function stamp(p_value timestamp with time zone)return varchar2;
 procedure load_state(p_actor varchar2,p_state out RRL_PICKER_TIME_STREAM%rowtype);
 function state_json(p_state RRL_PICKER_TIME_STREAM%rowtype)return json_object_t;
 procedure current_state(p_actor varchar2,p_result out clob);
 procedure read_window(p_actor varchar2,p_start varchar2,p_finish varchar2,p_result out clob);
end;
/
