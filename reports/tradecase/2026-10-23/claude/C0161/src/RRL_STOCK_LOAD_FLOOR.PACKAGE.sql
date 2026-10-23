package RRL_STOCK_LOAD_FLOOR authid definer
 accessible by(package RRL_STOCK_HU_LOAD_CORE,package RRL_STOCK_TRIP_DEPART_CMD,package RRL_TRANSPORT_PLAN_RULES,trigger RRL_LOAD_FLOOR_FACT_GUARD)as
 function compile_load(p_snapshot clob,p_vehicle number,p_rows in out nocopy json_array_t)return json_object_t;
 function checked_trip(p_trip number,p_vehicle number,p_extra_type number default null)return clob;
 function planning_counts(p_vehicle number,p_sts clob,p_base_counts clob,p_unknown number)return clob;
 procedure assert_load(p_vehicle number,p_trip number,p_frozen clob);
 procedure assert_departure(p_trip number,p_vehicle number,p_frozen clob);
 procedure persist_confirmation(p_operation varchar2,p_domain clob,p_actor varchar2);
 procedure assert_writing(p_operation varchar2);
end;