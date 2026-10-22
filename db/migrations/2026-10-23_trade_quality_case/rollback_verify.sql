declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_TRADE_QUALITY_CASE','RRL_TRADE_QUALITY_CASE_UNIT','RRL_TRADE_QUALITY_CASE_EVENT','RRL_TRADE_QUALITY_CASE_SQ','RRL_TRADE_QUALITY_CASE_API','RRL_TRADE_QUALITY_CASE_EVENT_APPEND','RRL_TRADE_QUALITY_CASE_UNIT_FROZEN');
 if n<>0 then raise_application_error(-20999,'QUALITY_OBJECTS_REMAIN');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
