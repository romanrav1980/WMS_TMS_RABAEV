@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_DELIVERY_TIME_API';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_NAMESPACE');end if;end;
/
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_DELIVERY_WINDOW','RRL_DELIVERY_ARRIVAL','RRL_DELIV_WINDOW_GUARD','RRL_DELIV_ARRIVAL_GUARD','RRL_DELIV_WINDOW_WARE_IX','RRL_DELIV_ARRIVAL_WARE_IX');
 if n!=0 then raise_application_error(-20886,'DELIVERY_TIME_NAMESPACE');end if;
 select count(*)into n from ALL_CONTEXT where NAMESPACE='RRL_DELIVERY_TIME_CTX';
 if n!=0 then raise_application_error(-20886,'DELIVERY_TIME_CONTEXT_NAMESPACE');end if;
end;
/
