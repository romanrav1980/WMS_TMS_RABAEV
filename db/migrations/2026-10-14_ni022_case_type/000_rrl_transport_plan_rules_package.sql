create or replace package RRL_TRANSPORT_PLAN_RULES authid definer as
 procedure assert_actor(p_actor varchar2,p_ware number);
 procedure check_vehicle(p_vehicle_id number,p_sts clob,p_complete number,p_result out clob);
end;

/
