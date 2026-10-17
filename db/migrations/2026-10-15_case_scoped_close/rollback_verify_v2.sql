@@known_sources_guard_raw.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_CASE_LIFECYCLE_API'or STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_ROLLBACK_OBJECTS');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_ROLLBACK_ERRORS');end if;
end;
/
