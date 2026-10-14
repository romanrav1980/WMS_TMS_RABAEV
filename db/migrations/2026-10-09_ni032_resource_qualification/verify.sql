declare n number;
begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_TASK_RESOURCE_POLICY','RRL_STOCK_SHORT_RECOVERY','RRL_STOCK_TASK_CORE','RRL_STOCK_METADATA_TX') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'QUALIFICATION_PACKAGES_INVALID');end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_RESOURCE_TASK_QUAL';
 if n!=1 then raise_application_error(-20808,'QUALIFICATION_TABLE_MISSING');end if;
end;
/
