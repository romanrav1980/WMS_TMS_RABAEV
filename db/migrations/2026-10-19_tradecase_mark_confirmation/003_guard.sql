create or replace trigger RRL_TRADE_MARK_WRITE_G before insert or update or delete on RRL_TRADE_MARK_EVENT
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_STOCK_WRITE_FORBIDDEN');end if;
end;
/
