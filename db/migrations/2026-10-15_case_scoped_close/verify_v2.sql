@@known_sources_guard_raw.sql
@@after_source_guard.sql
declare n number;begin
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_CURRENT_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'CASE_CLOSE_GLOBAL_INVALID');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_CASE_LIFECYCLE_API'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY')and STATUS='VALID';if n!=2 then raise_application_error(-20886,'CASE_CLOSE_PACKAGE_PAIR');end if;
end;
/
