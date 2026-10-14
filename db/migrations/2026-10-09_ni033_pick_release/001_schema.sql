declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PICK_WAVE' and COLUMN_NAME='PICK_RELEASED_AT';
 if n=0 then execute immediate 'alter table RRL_PICK_WAVE add (PICK_RELEASED_AT timestamp with time zone,PICK_RELEASED_BY varchar2(50),PICK_RELEASE_OPERATION_ID varchar2(100))';end if;
end;
/
