declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_WAREHOUSE_TASK' and COLUMN_NAME='STARTED_AT_INSTANT';
 if n=0 then execute immediate 'alter table RRL_WAREHOUSE_TASK add(STARTED_AT_INSTANT timestamp with time zone,STARTED_SHIFT_TIME_ZONE varchar2(64))';end if;
end;
/
