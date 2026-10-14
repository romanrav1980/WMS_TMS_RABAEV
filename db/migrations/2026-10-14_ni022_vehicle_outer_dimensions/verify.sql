declare n number;begin
 select count(*)into n from USER_ERRORS where NAME='RRL_VEHICLE_PROFILE_API';
 if n>0 then raise_application_error(-20808,'VEHICLE_OUTER_COMPILE_ERRORS');end if;
 select count(*)into n from USER_OBJECTS where OBJECT_NAME='RRL_VEHICLE_PROFILE_API'and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'VEHICLE_OUTER_INVALID');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_VEHICLE_PROFILE_HIST'and COLUMN_NAME in('OUTER_HEIGHT_MM','OUTER_LENGTH_MM')and DATA_TYPE='NUMBER'and DATA_PRECISION=7 and DATA_SCALE=0;
 if n!=2 then raise_application_error(-20808,'VEHICLE_OUTER_COLUMNS_MISSING');end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME in('RRL_VEH_OUTER_HEIGHT_CK','RRL_VEH_OUTER_LENGTH_CK')and STATUS='ENABLED'and VALIDATED='VALIDATED';
 if n!=2 then raise_application_error(-20808,'VEHICLE_OUTER_CONSTRAINTS_MISSING');end if;
end;
/
