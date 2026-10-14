create or replace package RRL_STOCK_LOAD_THERMAL authid definer
 accessible by(package RRL_STOCK_HU_LOAD_CORE,package RRL_STOCK_TRIP_DEPART_CMD,trigger RRL_LOAD_THERMAL_FACT_GUARD) as
 procedure compile_confirmation(p_members clob,p_vehicle number,p_context clob,p_domain out json_object_t);
 procedure assert_current(p_members clob,p_vehicle number,p_domain clob);
 procedure persist_confirmation(p_operation varchar2,p_domain clob,p_actor varchar2);
 procedure assert_writing(p_operation varchar2);
end;
/
