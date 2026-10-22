declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_VISIT','RRL_YARD_VISIT_EVENT','RRL_YARD_VISIT_SQ','RRL_YARD_VISIT_API','RRL_YARD_VISIT_EVENT_APPEND');
 if n<>0 then raise_application_error(-20999,'YARD_OBJECTS_REMAIN');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
end;
/
