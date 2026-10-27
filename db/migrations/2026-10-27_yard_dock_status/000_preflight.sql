declare n number;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_YARD_DOCK_STATUS_EVENT','RRL_YARD_DOCK_STATUS_API','RRL_YARD_DOCK_STATUS_EVENT_APPEND');
 if n<>0 then raise_application_error(-20999,'DOCK_STATUS_OBJECT_EXISTS');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_DOCK' and COLUMN_NAME in('WARE_ID','DOCK','DOCK_IS_BLOCKED');
 if n<>3 then raise_application_error(-20999,'DOCK_SCHEMA_DRIFT');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_BEFORE');end if;
end;
/
