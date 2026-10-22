declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME='RRL_TRADE_EXTRA_STOP_API';if n<>0 then raise_application_error(-20999,'EXTRA_STOP_COMPILE_ERRORS');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_TRADE_ROUTE_STOP_POLICY','RRL_TRADE_EXTRA_STOP_EVENT');
 if n<>2 then raise_application_error(-20999,'EXTRA_STOP_TABLES_MISSING');end if;
 select count(*)into n from USER_TRIGGERS where TRIGGER_NAME='RRL_TRADE_EXTRA_STOP_EVENT_APPEND'and STATUS='ENABLED';
 if n<>1 then raise_application_error(-20999,'EXTRA_STOP_APPEND_GUARD_MISSING');end if;
end;
/
