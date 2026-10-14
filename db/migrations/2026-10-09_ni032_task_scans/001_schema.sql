declare n number;
begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_TASK_SCAN_DRAFT';
 if n=0 then execute immediate 'create table RRL_TASK_SCAN_DRAFT(
 DRAFT_ID varchar2(100) not null,TASK_ID number not null,ACTOR varchar2(100) not null,
 REQUEST_JSON clob not null,UNIT_KEYS_JSON clob not null,PROFILE_SIGNATURE varchar2(64) not null,
 STOCK_VERSION number not null,SOURCE_UID varchar2(50) not null,SOURCE_CELL varchar2(15) not null,
 BASE_QUANTITY number not null,CREATED_AT timestamp default systimestamp not null,
 constraint RRL_TASK_SCAN_DRAFT_PK primary key(DRAFT_ID),
 constraint RRL_TASK_SCAN_DRAFT_FK foreign key(TASK_ID) references RRL_WAREHOUSE_TASK(TASK_ID),
 constraint RRL_TASK_SCAN_DRAFT_CK check(BASE_QUANTITY>0))';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_TASK_SCAN_DRAFT_I';
 if n=0 then execute immediate 'create index RRL_TASK_SCAN_DRAFT_I on RRL_TASK_SCAN_DRAFT(TASK_ID,ACTOR,CREATED_AT)';end if;
end;
/
create or replace trigger RRL_TASK_SCAN_IMMUTABLE
 before update or delete on RRL_TASK_SCAN_DRAFT
begin
 raise_application_error(-20885,'IMMUTABLE_TASK_SCAN_DRAFT');
end;
/
