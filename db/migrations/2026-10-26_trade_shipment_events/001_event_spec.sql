create or replace package RRL_TRADE_SHIP_EVENT authid definer accessible by(package RRL_STOCK_TRIP_DEPART_CMD)as
 procedure publish(p_operation varchar2,p_trip number);
end;

/
