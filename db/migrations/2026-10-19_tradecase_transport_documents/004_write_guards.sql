create or replace trigger RRL_TRADE_TRIP_LINK_G before insert or update or delete on RRL_TRADE_TRIP_LINK
begin if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_TRANSPORT_WRITE_FORBIDDEN');end if;end;
/
create or replace trigger RRL_TRADE_TRIP_DOC_G before insert or update or delete on RRL_TRADE_TRIP_DOC_EVENT
begin if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_TRANSPORT_WRITE_FORBIDDEN');end if;end;
/
