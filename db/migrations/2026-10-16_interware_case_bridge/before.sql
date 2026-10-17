@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_IW_CASE_BRIDGE';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_NAMESPACE');end if;end;
/
declare n number;begin select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_IW_CASE_CARRIER','RRL_IW_CASE_CARRIER_GUARD','RRL_IW_GREC_SOURCE_ST_IX');if n!=0 then raise_application_error(-20886,'CASE_BRIDGE_NAMESPACE');end if;end;
/
