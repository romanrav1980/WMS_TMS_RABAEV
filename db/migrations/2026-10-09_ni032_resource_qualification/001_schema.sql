-- Add explicit qualifications and observed session locations to existing resources.
declare n number;
begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_RESOURCE_TASK_QUAL';
 if n=0 then execute immediate 'create table RRL_RESOURCE_TASK_QUAL(
 RESOURCE_ID number not null,TASK_TYPE varchar2(40) not null,
 VALID_FROM timestamp default systimestamp not null,VALID_UNTIL timestamp,
 ACTIVE number default 1 not null,UPDATED_BY varchar2(100),UPDATED_AT timestamp default systimestamp not null,
 constraint RRL_RESOURCE_TASK_QUAL_PK primary key(RESOURCE_ID,TASK_TYPE),
 constraint RRL_RESOURCE_TASK_QUAL_FK foreign key(RESOURCE_ID) references RRL_RESOURCE(RESOURCE_ID),
 constraint RRL_RESOURCE_TASK_QUAL_CK check(ACTIVE in(0,1) and (VALID_UNTIL is null or VALID_UNTIL>VALID_FROM)))';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RESOURCE_SESSION' and COLUMN_NAME='LAST_CELL';
 if n=0 then execute immediate 'alter table RRL_RESOURCE_SESSION add LAST_CELL varchar2(15)';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RESOURCE_SESSION' and COLUMN_NAME='LAST_POSITION_AT';
 if n=0 then execute immediate 'alter table RRL_RESOURCE_SESSION add LAST_POSITION_AT timestamp';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RESOURCE_SESSION' and COLUMN_NAME='CURRENT_INVENTORY_TASK_ID';
 if n=0 then execute immediate 'alter table RRL_RESOURCE_SESSION add CURRENT_INVENTORY_TASK_ID number';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_INVENTORY_TASK' and COLUMN_NAME='RESOURCE_SESSION_ID';
 if n=0 then execute immediate 'alter table RRL_INVENTORY_TASK add RESOURCE_SESSION_ID number';end if;
end;
/
