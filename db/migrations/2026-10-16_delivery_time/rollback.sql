@@after_sources.sql
declare n number;begin
 select count(*)into n from RRL_DELIVERY_WINDOW;if n!=0 then raise_application_error(-20886,'DELIVERY_TIME_RETAINED_PLAN');end if;
 select count(*)into n from RRL_DELIVERY_ARRIVAL;if n!=0 then raise_application_error(-20886,'DELIVERY_TIME_RETAINED_ARRIVAL');end if;
end;
/
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

drop trigger RRL_DELIV_ARRIVAL_GUARD;
drop trigger RRL_DELIV_WINDOW_GUARD;
drop context RRL_DELIVERY_TIME_CTX;
drop package RRL_DELIVERY_TIME_API;
drop table RRL_DELIVERY_ARRIVAL;
drop table RRL_DELIVERY_WINDOW;
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-delivery-time';
commit;
