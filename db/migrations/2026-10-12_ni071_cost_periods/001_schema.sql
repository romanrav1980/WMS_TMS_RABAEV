-- Existing recognised rows, including unknown legacy dates, remain untouched.
begin execute immediate 'alter table RRL_LOGISTICS_COST_LINE add PERIOD_KEY varchar2(10) default ''LEGACY'' not null';
exception when others then if sqlcode!=-1430 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOG_COST_SOURCE_CLAIM(
 LOAD_OPERATION_ID varchar2(100)not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 COST_CODE varchar2(40)not null,CURRENCY varchar2(3)not null,
 OPERATION_ID varchar2(100)not null references RRL_LOGISTICS_COST_RUN(OPERATION_ID),
 primary key(LOAD_OPERATION_ID,COST_CODE,CURRENCY),
 unique(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
insert into RRL_LOG_COST_SOURCE_CLAIM(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)
 select distinct l.LOAD_OPERATION_ID,l.COST_CODE,l.CURRENCY,l.OPERATION_ID from RRL_LOGISTICS_COST_LINE l
 where not exists(select 1 from RRL_LOG_COST_SOURCE_CLAIM s where s.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID and s.COST_CODE=l.COST_CODE and s.CURRENCY=l.CURRENCY);
commit;
/
declare n number;begin
 for k in(select CONSTRAINT_NAME,CONSTRAINT_TYPE from USER_CONSTRAINTS where TABLE_NAME='RRL_LOGISTICS_COST_LINE'and CONSTRAINT_TYPE in('P','U'))loop
  select count(*)into n from ALL_CONSTRAINTS where CONSTRAINT_TYPE='R'and R_OWNER=user and R_CONSTRAINT_NAME=k.CONSTRAINT_NAME;
  if n!=0 then raise_application_error(-20886,'COST_LINE_EXTERNAL_KEY_DEPENDENCY');end if;
  execute immediate 'alter table RRL_LOGISTICS_COST_LINE drop constraint '||dbms_assert.simple_sql_name(k.CONSTRAINT_NAME);
 end loop;
 execute immediate 'alter table RRL_LOGISTICS_COST_LINE add constraint RRL_LOG_COST_PERIOD_PK primary key(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE,PERIOD_KEY)';
 execute immediate 'alter table RRL_LOGISTICS_COST_LINE add constraint RRL_LOG_COST_PERIOD_UQ unique(LOAD_OPERATION_ID,COST_CODE,CURRENCY,PERIOD_KEY)';
 execute immediate 'alter table RRL_LOGISTICS_COST_LINE add constraint RRL_LOG_COST_SOURCE_FK foreign key(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)references RRL_LOG_COST_SOURCE_CLAIM(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)';
end;
/
