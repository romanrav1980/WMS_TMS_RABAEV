declare n number;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_DOCK_STATUS_EVENT','RRL_YARD_DOCK_STATUS_API','RRL_YARD_DOCK_STATUS_EVENT_APPEND') and STATUS='VALID';
 if n<3 then raise_application_error(-20999,'DOCK_STATUS_OBJECTS_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_YARD_DOCK_STATUS_API','RRL_YARD_DOCK_STATUS_EVENT_APPEND');
 if n<>0 then raise_application_error(-20999,'DOCK_STATUS_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_AFTER');end if;
end;
/
