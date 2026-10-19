create or replace trigger RRL_TRADE_BUYOUT_G before insert or update or delete on RRL_TRADE_BUYOUT
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_BUYOUT_WRITE_FORBIDDEN');end if;
end;
/
create or replace trigger RRL_TRADE_BUYOUT_UNIT_G before insert or update or delete on RRL_TRADE_BUYOUT_UNIT
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_BUYOUT_WRITE_FORBIDDEN');end if;
end;
/
create or replace trigger RRL_TRADE_BUYOUT_EVENT_G before insert or update or delete on RRL_TRADE_BUYOUT_EVENT
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_BUYOUT_WRITE_FORBIDDEN');end if;
end;
/
