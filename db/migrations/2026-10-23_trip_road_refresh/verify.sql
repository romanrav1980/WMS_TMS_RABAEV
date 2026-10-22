declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;
 select count(*)into n from USER_TRIGGERS where TRIGGER_NAME='RRL_TT_ROAD_REFRESH_APPEND'and STATUS='ENABLED';if n<>1 then raise_application_error(-20999,'ROAD_REFRESH_GUARD_MISSING');end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_TT_ROAD_REFRESH_PK'and STATUS='ENABLED';if n<>1 then raise_application_error(-20999,'ROAD_REFRESH_KEY_MISSING');end if;
end;
/