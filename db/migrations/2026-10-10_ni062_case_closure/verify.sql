declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_CASE_CLOSE','RRL_STOCK_STORE_CASE_CMD','RRL_STORE_CASE_APPEND_GUARD','RRL_STORE_CASE_CLOSE_GUARD')and STATUS!='VALID';if n>0 then raise_application_error(-20808,'STORE_CASE_CLOSURE_INVALID');end if;end;
/
