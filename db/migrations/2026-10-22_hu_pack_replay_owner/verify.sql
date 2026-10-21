declare n number;begin select count(*)into n from user_objects where STATUS='INVALID';if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;select count(*)into n from user_errors where NAME='RRL_HU_EXEC_ACCESS';if n<>0 then raise_application_error(-20999,'HU_EXEC_ERRORS');end if;end;
/
