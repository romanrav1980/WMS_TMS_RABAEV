declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_LOG_RATE_HISTORY_GUARD','RRL_LOG_COST_RUN_GUARD','RRL_LOG_COST_LINE_GUARD')and STATUS!='VALID';if n>0 then raise_application_error(-20808,'LOGISTICS_COST_INVALID');end if;end;
/
