create or replace trigger RRL_TRADE_ATTR_WRITE_G before insert or update or delete on RRL_TRADE_STOCK_ATTR
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_STOCK_WRITE_FORBIDDEN');end if;
end;
/
create or replace trigger RRL_TRADE_CELL_WRITE_G before insert or update or delete on RRL_TRADE_CELL_POLICY
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_STOCK_WRITE_FORBIDDEN');end if;
end;
/
create or replace trigger RRL_TRADE_OWNER_WRITE_G before insert or update or delete on RRL_TRADE_OWNER_GRANT
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_STOCK_WRITE_FORBIDDEN');end if;
end;
/
create or replace trigger RRL_TRADE_CMD_WRITE_G before insert or update or delete on RRL_TRADE_STOCK_COMMAND
begin
 if RRL_TRADE_STOCK_API.writes_allowed<>1 then raise_application_error(-20863,'TRADE_STOCK_WRITE_FORBIDDEN');end if;
end;
/
