create or replace package RRL_DELIVERY_TIME_API as
 procedure plan_window(p_request clob,p_actor varchar2,p_result out clob);
 procedure record_arrival(p_request clob,p_actor varchar2,p_result out clob);
 procedure read_times(p_load varchar2,p_store varchar2,p_actor varchar2,p_result out clob);
end;
/
