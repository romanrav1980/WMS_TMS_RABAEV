@@003_projector.sql
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_FORECAST_PROJECTOR','RRL_FORECAST_SOURCE_RULES')and STATUS!='VALID';
 if n!=0 then raise_application_error(-20899,'FORECAST133_INVALID_OBJECTS');end if;
end;
/
