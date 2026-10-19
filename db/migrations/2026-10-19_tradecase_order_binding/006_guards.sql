create or replace trigger RRL_TRADE_ORDER_LINK_G before insert or update or delete on RRL_TRADE_ORDER_LINK
begin
 if RRL_TRADE_ORDER_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_ORDER_WRITE_FORBIDDEN');end if;
end;
/
create or replace trigger RRL_TRADE_ORDER_LINE_G before insert or update or delete on RRL_TRADE_ORDER_LINE
begin
 if RRL_TRADE_ORDER_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_ORDER_WRITE_FORBIDDEN');end if;
end;
/
create or replace trigger RRL_TRADE_ORDER_CMD_G before insert or update or delete on RRL_TRADE_ORDER_COMMAND
begin
 if RRL_TRADE_ORDER_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_ORDER_WRITE_FORBIDDEN');end if;
end;
/
