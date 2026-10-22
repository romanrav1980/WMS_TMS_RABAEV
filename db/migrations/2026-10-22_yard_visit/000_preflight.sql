declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_VISIT','RRL_YARD_VISIT_EVENT','RRL_YARD_VISIT_SQ','RRL_YARD_VISIT_API','RRL_YARD_VISIT_EVENT_APPEND');
 if n<>0 then raise_application_error(-20999,'YARD_OBJECTS_ALREADY_PRESENT');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_TRADE_SITE','RRL_ACCESS_REV','RRL_TT_DOCK','RRL_TRANSPORT_TASK','RRL_TRADE_TRIP_LINK','RRL_TRADE_DOCUMENT');
 if n<>6 then raise_application_error(-20999,'YARD_DEPENDENCIES_MISSING');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
