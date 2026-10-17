@@after_source_guard.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WH_EMPTY_GLOBAL_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'WH_EMPTY_CURRENT_ERRORS');end if;
end;
/
