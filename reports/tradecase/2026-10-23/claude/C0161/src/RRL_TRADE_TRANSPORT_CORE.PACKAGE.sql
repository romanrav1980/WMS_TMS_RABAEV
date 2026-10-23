package RRL_TRADE_TRANSPORT_CORE authid definer accessible by(package RRL_TRADE_STOCK_API,package RRL_STOCK_TRIP_DEPART_CMD)as
 procedure bind_trip(p_ware number,p_actor varchar2,j json_object_t,r in out nocopy json_object_t);
 procedure confirm_document(p_ware number,p_actor varchar2,j json_object_t,r in out nocopy json_object_t);
 procedure read_state(p_ware number,p_actor varchar2,j json_object_t,p_result out clob);
 procedure assert_departure(p_trip number);
end;