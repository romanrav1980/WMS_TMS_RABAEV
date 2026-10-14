-- CCTV archive links are separate from warehouse-map chambers ("camera" cuboids).
declare n number;
 procedure column_if_missing(p_name varchar2,p_type varchar2) is begin
  select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_SHORT' and COLUMN_NAME=p_name;
  if n=0 then execute immediate 'alter table RRL_CASE_PICK_SHORT add '||p_name||' '||p_type;end if;
 end;
begin
 column_if_missing('INVESTIGATION_VERSION','number default 0 not null');
 column_if_missing('INVESTIGATION_STATUS','varchar2(12) default ''OPEN'' not null');
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_SHORT_INV_STATUS_C';
 if n=0 then execute immediate 'alter table RRL_CASE_PICK_SHORT add constraint RRL_SHORT_INV_STATUS_C check(INVESTIGATION_STATUS in(''OPEN'',''REVIEWING'',''CLOSED''))';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_CCTV_VIEWPOINT';
 if n=0 then execute immediate 'create table RRL_CCTV_VIEWPOINT(
  WARE_ID number not null,CELL_CODE varchar2(60) not null,VIEWPOINT_CODE varchar2(80) not null,
  ARCHIVE_URI_TEMPLATE varchar2(2000) not null,STORED_TIME_OFFSET varchar2(6) default ''+03:00'' not null,
  BEFORE_SECONDS number default 120 not null,AFTER_SECONDS number default 120 not null,
  ACTIVE number default 1 not null,POLICY_VERSION number default 1 not null,
  UPDATED_AT timestamp default systimestamp not null,UPDATED_BY varchar2(100) not null,
  constraint RRL_CCTV_VIEWPOINT_PK primary key(WARE_ID,CELL_CODE,VIEWPOINT_CODE),
  constraint RRL_CCTV_ACTIVE_C check(ACTIVE in(0,1)),
  constraint RRL_CCTV_WINDOW_C check(BEFORE_SECONDS between 0 and 3600 and AFTER_SECONDS between 0 and 3600),
  constraint RRL_CCTV_VERSION_C check(POLICY_VERSION>=1))';end if;
end;
/
