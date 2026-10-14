declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_SHORT' and COLUMN_NAME='CREATED_AT_INSTANT';
 -- Add without a default first: historical rows must not acquire a fictional current incident time.
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_SHORT add CREATED_AT_INSTANT timestamp with time zone';end if;
 execute immediate 'alter table RRL_CASE_PICK_SHORT modify CREATED_AT_INSTANT default systimestamp';
end;
/
