declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_INTERWARE_PLAN_GUARD','RRL_STORE_INTERWARE_LEG_GUARD','RRL_STOCK_METADATA_TX')and STATUS!='VALID';if n>0 then raise_application_error(-20808,'INTERWARE_PLAN_INVALID');end if;end;
/
