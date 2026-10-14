create or replace package RRL_STOCK_HU_LOAD_CORE authid definer accessible by(package RRL_STOCK_HU_SHIP_CMD,package RRL_STOCK_TRIP_DEPART_CMD,package RRL_STOCK_SINGLE_LOAD_CMD,package RRL_STOCK_LOAD_RECONCILE_CMD) as
 procedure compile_load(p_request clob,p_snapshot clob,p_shipments clob,f in out nocopy json_array_t,r in out nocopy json_array_t,p_domain out json_object_t);
 procedure begin_load(p_domain clob);
 procedure finish_load(p_domain clob,p_snapshot clob,p_operation varchar2,p_actor varchar2);
end;
/
