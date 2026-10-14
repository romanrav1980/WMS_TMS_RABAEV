declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_CASE_RESOURCE_POLICY','RRL_TASK_RESOURCE_POLICY','RRL_STOCK_CASE_PICK_CMD','RRL_STOCK_TASK_PLAN','RRL_STOCK_METADATA_TX') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'CASE_RESOURCE_PACKAGES_INVALID');end if;
 select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_CASE_RESOURCE_POLICY' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=2 then raise_application_error(-20808,'CASE_RESOURCE_POLICY_MISSING');end if;
end;
/
