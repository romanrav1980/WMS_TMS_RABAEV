create or replace package RRL_VEHICLE_PROFILE_API authid definer as
 procedure configure(p_request clob,p_actor varchar2,p_result out clob);
 function describe_profile(p_vehicle number)return clob;
 procedure assert_writing;
 function check_floor_capacity(p_vehicle number,p_counts clob,p_unknown number)return clob;
end;
/
