declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME='RRL_YARD_VISIT_API';if n<>0 then raise_application_error(-20999,'YARD_COMPILE_ERRORS');end if;
 select count(*)into n from USER_TABLES where TABLE_NAME in('RRL_YARD_VISIT','RRL_YARD_VISIT_EVENT');if n<>2 then raise_application_error(-20999,'YARD_TABLES_MISSING');end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME in('RRL_YARD_VISIT_DOCK_UK','RRL_YARD_VISIT_VEHICLE_UK','RRL_YARD_VISIT_TRIP_UK')and UNIQUENESS='UNIQUE';
 if n<>3 then raise_application_error(-20999,'YARD_OCCUPANCY_GUARDS_MISSING');end if;
 select count(*)into n from USER_TRIGGERS where TRIGGER_NAME='RRL_YARD_VISIT_EVENT_APPEND'and STATUS='ENABLED';
 if n<>1 then raise_application_error(-20999,'YARD_EVENT_APPEND_GUARD_MISSING');end if;
end;
/
