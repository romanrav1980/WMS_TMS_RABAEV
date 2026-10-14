declare n number;begin
 select count(*) into n from RRL_RESOURCE_TYPE where RESOURCE_TYPE in('REACHTRUCK','FORKLIFT') and instr(','||replace(DEFAULT_TASK_TYPES,' ','')||',',',PUTAWAY,')>0;
 if n!=2 then raise_application_error(-20808,'PUTAWAY_TYPE_CAPABILITY_MISSING');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_TASK_RESOURCE_POLICY' and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'WAREHOUSE_RESOURCE_POLICY_INVALID');end if;
end;
/
