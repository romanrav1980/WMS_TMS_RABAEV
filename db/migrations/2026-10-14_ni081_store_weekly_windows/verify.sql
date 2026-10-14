-- MIGRATION_ID: 2026-10-14-ni081-store-weekly-windows
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_WINDOW_RULES','RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API')and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'STORE_WEEKLY_PACKAGES_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_STORE_WINDOW_RULES','RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API')and ATTRIBUTE='ERROR';
 if n>0 then raise_application_error(-20808,'STORE_WEEKLY_COMPILATION_ERRORS');end if;
end;
/
