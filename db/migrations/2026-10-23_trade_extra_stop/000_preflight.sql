declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRADE_ROUTE_STOP_POLICY','RRL_TRADE_EXTRA_STOP_EVENT','RRL_TRADE_EXTRA_STOP_API','RRL_TRADE_EXTRA_STOP_EVENT_APPEND');
 if n<>0 then raise_application_error(-20999,'EXTRA_STOP_OBJECTS_ALREADY_PRESENT');end if;
 -- Only existing owners are called; none of them is replaced by this migration.
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TT_TIME_API','RRL_TT_ROUTE_SCHEDULE','RRL_STORE_WINDOW_RULES','RRL_ACCESS_API','RRL_STOCK_PLAN_HELPER')
  and OBJECT_TYPE='PACKAGE BODY'and STATUS='VALID';
 if n<>5 then raise_application_error(-20999,'EXTRA_STOP_DEPENDENCIES_MISSING');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_TRANSPORT_TASK','RRL_SBORKA_PALLETS','RRL_ADDR','RRL_ADDR_DISTANCE_MATRIX');
 if n<>4 then raise_application_error(-20999,'EXTRA_STOP_TABLES_MISSING');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
