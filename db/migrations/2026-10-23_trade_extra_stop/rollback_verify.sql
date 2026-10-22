declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRADE_ROUTE_STOP_POLICY','RRL_TRADE_EXTRA_STOP_EVENT','RRL_TRADE_EXTRA_STOP_API','RRL_TRADE_EXTRA_STOP_EVENT_APPEND');
 if n<>0 then raise_application_error(-20999,'EXTRA_STOP_OBJECTS_REMAIN');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
