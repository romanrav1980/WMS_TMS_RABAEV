declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME in('RRL_STORE_PROFILE','RRL_STORE_RECEIVING_WINDOW','RRL_STORE_PROFILE_CHANGE');
 if n!=3 then raise_application_error(-20808,'STORE_PROFILE_TABLES_MISSING');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_PROFILE_GUARD','RRL_STORE_RECEIVING_WINDOW_GUARD','RRL_STORE_PROFILE_CHANGE_GUARD') and STATUS='VALID';
 if n!=3 then raise_application_error(-20808,'STORE_PROFILE_GUARDS_INVALID');end if;
 select count(*) into n from USER_ERRORS where NAME in('RRL_STORE_PROFILE_GUARD','RRL_STORE_RECEIVING_WINDOW_GUARD','RRL_STORE_PROFILE_CHANGE_GUARD');
 if n>0 then raise_application_error(-20808,'STORE_PROFILE_COMPILE_ERRORS');end if;
end;
/
