declare n number;begin
 select count(*)into n from USER_ERRORS where NAME in('RRL_STORE_ACCESS_RULES','RRL_TRANSPORT_PLAN_RULES','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD');
 if n>0 then raise_application_error(-20808,'STORE_ACCESS_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_ACCESS_RULES','RRL_TRANSPORT_PLAN_RULES','RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD')and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'STORE_ACCESS_INVALID');end if;
 select count(*)into n from USER_SOURCE where TYPE='PACKAGE BODY'and NAME in('RRL_STOCK_HU_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD')and upper(TEXT)like '%RRL_STORE_ACCESS_RULES.ASSERT_MEMBERS%';
 if n!=2 then raise_application_error(-20808,'STORE_ACCESS_FINAL_CALLS_MISSING');end if;
 select count(*)into n from USER_SOURCE where TYPE='PACKAGE BODY'and NAME='RRL_TRANSPORT_PLAN_RULES'and upper(TEXT)like '%RRL_STORE_ACCESS_RULES.CHECK_STS%';
 if n!=1 then raise_application_error(-20808,'STORE_ACCESS_PLAN_CALL_MISSING');end if;
end;
/
