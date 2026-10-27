declare n number;
begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_DOCK_STATUS_EVENT','RRL_YARD_DOCK_STATUS_API','RRL_YARD_DOCK_STATUS_EVENT_APPEND');
 if n<>0 then raise_application_error(-20999,'DOCK_STATUS_OBJECT_REMAINS');end if;
end;
/
