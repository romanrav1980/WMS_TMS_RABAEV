begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
declare n number;begin
 select count(*)into n from user_errors where NAME in('RRL_STOCK_TASK_CORE','RRL_TRADE_STOCK_GUARD','RRL_TRADE_PICK_CONTEXT');
 if n<>0 then raise_application_error(-20999,'TRADE_FULLPAL_CONTEXT_COMPILE');end if;
 select count(*)into n from user_objects where STATUS='INVALID';
 if n<>0 then raise_application_error(-20999,'INVALID_OBJECTS');end if;end;
/
