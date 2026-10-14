declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_SHORT_RECOVERY','RRL_STOCK_CASE_PICK_CMD','RRL_STOCK_WAVE_CMD') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'RECOVERY_CHUNK_PACKAGES_INVALID');end if;
end;
/
