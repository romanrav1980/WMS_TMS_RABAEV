declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_RETURN_DISPOSE','RRL_STOCK_EFFECT_CORE','RRL_STOCK_POSTING_API','RRL_DISPOSAL_REQUEST_GUARD','RRL_DISPOSAL_FACT_GUARD')and STATUS!='VALID';if n>0 then raise_application_error(-20808,'RETURN_DISPOSAL_INVALID');end if;end;
/
