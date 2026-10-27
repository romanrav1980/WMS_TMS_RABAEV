declare n number;begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20886,'GROUPED_ST_WRONG_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'GROUPED_ST_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'GROUPED_ST_ERRORS');end if;
end;
/
@@before_sources.sql
