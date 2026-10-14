declare n number;
 procedure column_if_missing(p_name varchar2,p_type varchar2) is begin
  select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RESOURCE_SHIFT' and COLUMN_NAME=p_name;
  if n=0 then execute immediate 'alter table RRL_RESOURCE_SHIFT add '||p_name||' '||p_type;end if;
 end;
 procedure constraint_if_missing(p_name varchar2,p_sql varchar2) is begin
  select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME=p_name;
  if n=0 then execute immediate p_sql;end if;
 end;
begin
 column_if_missing('BASE_SHIFT_ID','number');
 column_if_missing('REACH_SHIFT_ROLE','varchar2(10) default ''GENERAL'' not null');
 column_if_missing('EXPECTED_DRIVERS','number');
 constraint_if_missing('RRL_SHIFT_REACH_ROLE_C','alter table RRL_RESOURCE_SHIFT add constraint RRL_SHIFT_REACH_ROLE_C check(REACH_SHIFT_ROLE in(''GENERAL'',''MAIN'',''DUTY''))');
 constraint_if_missing('RRL_SHIFT_REACH_BASE_F','alter table RRL_RESOURCE_SHIFT add constraint RRL_SHIFT_REACH_BASE_F foreign key(BASE_SHIFT_ID) references RRL_RESOURCE_SHIFT(SHIFT_ID)');
 constraint_if_missing('RRL_SHIFT_REACH_DRIVERS_C','alter table RRL_RESOURCE_SHIFT add constraint RRL_SHIFT_REACH_DRIVERS_C check(EXPECTED_DRIVERS is null or (EXPECTED_DRIVERS=trunc(EXPECTED_DRIVERS) and EXPECTED_DRIVERS between 1 and 200 and (REACH_SHIFT_ROLE!=''DUTY'' or EXPECTED_DRIVERS<=2)))');
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_SHIFT_REACH_BASE_U';
 if n=0 then execute immediate 'create unique index RRL_SHIFT_REACH_BASE_U on RRL_RESOURCE_SHIFT(case when BASE_SHIFT_ID is not null then BASE_SHIFT_ID end,case when BASE_SHIFT_ID is not null then REACH_SHIFT_ROLE end)';end if;
end;
/
