@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/
declare n number;begin
 select count(*)into n from ALL_CONTEXT where NAMESPACE='RRL_DELIVERY_TIME_CTX'and SCHEMA='RABAEV'and PACKAGE='RRL_DELIVERY_TIME_API';
 if n!=1 then raise_application_error(-20886,'DELIVERY_TIME_CONTEXT_OWNER');end if;
 select count(*)into n from USER_CONSTRAINTS where TABLE_NAME in('RRL_DELIVERY_WINDOW','RRL_DELIVERY_ARRIVAL')and(STATUS!='ENABLED'or VALIDATED!='VALIDATED');
 if n!=0 then raise_application_error(-20886,'DELIVERY_TIME_CONSTRAINTS');end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME in('RRL_DELIV_WINDOW_WARE_IX','RRL_DELIV_ARRIVAL_WARE_IX')and STATUS='VALID';
 if n!=2 then raise_application_error(-20886,'DELIVERY_TIME_INDEXES');end if;
end;
/
