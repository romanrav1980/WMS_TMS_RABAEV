prompt [09] Schema contract patch

declare
  v_count number;
begin
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ORDERS' and column_name = 'COND';
  if v_count = 0 then execute immediate 'alter table RRL_ORDERS add (COND NUMBER default 0)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ORDERS' and column_name = 'ORD1';
  if v_count = 0 then execute immediate 'alter table RRL_ORDERS add (ORD1 NUMBER default 0)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ORDER_ROWS' and column_name = 'MOD_ID';
  if v_count = 0 then execute immediate 'alter table RRL_ORDER_ROWS add (MOD_ID NUMBER default 0)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ORDER_ROWS' and column_name = 'QUANTITY_PLANNED';
  if v_count = 0 then execute immediate 'alter table RRL_ORDER_ROWS add (QUANTITY_PLANNED NUMBER default 0)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ORDER_ROWS' and column_name = 'PARTIONPLANNED';
  if v_count = 0 then execute immediate 'alter table RRL_ORDER_ROWS add (PARTIONPLANNED VARCHAR2(50))'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ARTICUL_MODS' and column_name = 'SHK_SHT';
  if v_count = 0 then execute immediate 'alter table RRL_ARTICUL_MODS add (SHK_SHT VARCHAR2(255))'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ARTICUL_MODS' and column_name = 'SHK_KOR';
  if v_count = 0 then execute immediate 'alter table RRL_ARTICUL_MODS add (SHK_KOR VARCHAR2(255))'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ARTICUL_MODS' and column_name = 'DIMK_X';
  if v_count = 0 then execute immediate 'alter table RRL_ARTICUL_MODS add (DIMK_X NUMBER)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ARTICUL_MODS' and column_name = 'DIMK_Y';
  if v_count = 0 then execute immediate 'alter table RRL_ARTICUL_MODS add (DIMK_Y NUMBER)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ARTICUL_MODS' and column_name = 'DIMK_Z';
  if v_count = 0 then execute immediate 'alter table RRL_ARTICUL_MODS add (DIMK_Z NUMBER)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ARTICUL_MODS' and column_name = 'BRT_WEIGHT_OF_KOR';
  if v_count = 0 then execute immediate 'alter table RRL_ARTICUL_MODS add (BRT_WEIGHT_OF_KOR NUMBER)'; end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_ARTICULS' and column_name = 'UUZ';
  if v_count = 0 then execute immediate 'alter table RRL_ARTICULS add (UUZ NUMBER default 0)'; end if;
end;
/

create or replace trigger RRL_ORDER_ROWS_TRG
before insert on RRL_ORDER_ROWS
for each row
begin
  if :new.ID is null then
    select RRL_ORDER_ROWS_SQ.nextval into :new.ID from dual;
  end if;
end;
/

declare
  v_count number;
begin
  select count(*) into v_count from user_tables where table_name = 'RRL_TT_GLOBAL_MESS';
  if v_count = 0 then
    execute immediate 'create table RRL_TT_GLOBAL_MESS (ID NUMBER not null, MESS VARCHAR2(250))';
    execute immediate 'alter table RRL_TT_GLOBAL_MESS add constraint RRL_TT_GLOBAL_MESS_PK primary key (ID)';
  end if;

  select count(*) into v_count from user_tables where table_name = 'RRL_TYPE_PALL';
  if v_count = 0 then
    execute immediate 'create table RRL_TYPE_PALL (ID NUMBER not null, NAME VARCHAR2(100 CHAR) not null)';
    execute immediate 'alter table RRL_TYPE_PALL add constraint RRL_TYPE_PALL_PK primary key (ID)';
    execute immediate 'create unique index RRL_TYPE_PALL_U1 on RRL_TYPE_PALL (NAME)';
  else
    execute immediate 'alter table RRL_TYPE_PALL modify (NAME VARCHAR2(100 CHAR))';
  end if;

  select count(*) into v_count from user_tables where table_name = 'RRL_TOVARO_NOSITEL';
  if v_count = 0 then
    execute immediate 'create table RRL_TOVARO_NOSITEL (ID VARCHAR2(50) not null, TYPE_TN NUMBER not null, NAME VARCHAR2(255))';
    execute immediate 'alter table RRL_TOVARO_NOSITEL add constraint RRL_TOVARO_NOSITEL_PK primary key (ID)';
    execute immediate 'create index RRL_TOVARO_NOSITEL_I1 on RRL_TOVARO_NOSITEL (TYPE_TN)';
  end if;

  select count(*) into v_count from user_tables where table_name = 'RRL_COMPL_RESERVE';
  if v_count = 0 then
    execute immediate q'[
      create table RRL_COMPL_RESERVE (
        ID         NUMBER not null,
        ARTICUL    VARCHAR2(50),
        PARTIONID  VARCHAR2(250),
        QTY        NUMBER,
        ORDERID    NUMBER,
        ORDERROWID NUMBER,
        CONDITION  NUMBER,
        EXPDATE    DATE,
        MOD_ID     NUMBER,
        WARE_ID    NUMBER
      )
    ]';
    execute immediate 'alter table RRL_COMPL_RESERVE add constraint RRL_COMPL_RESERVE_PK primary key (ID)';
    execute immediate 'create index RRL_COMPL_RESERVE_I1 on RRL_COMPL_RESERVE (ARTICUL, WARE_ID)';
    execute immediate 'create index RRL_COMPL_RESERVE_I2 on RRL_COMPL_RESERVE (ORDERID, ORDERROWID)';
    execute immediate 'create index RRL_COMPL_RESERVE_I3 on RRL_COMPL_RESERVE (PARTIONID)';
  end if;

  select count(*) into v_count from user_sequences where sequence_name = 'RRL_COMPL_RESERVE_SQ';
  if v_count = 0 then execute immediate 'create sequence RRL_COMPL_RESERVE_SQ start with 1 increment by 1 nocache'; end if;
end;
/

insert into RRL_TT_GLOBAL_MESS (ID, MESS)
select 1, '' from dual where not exists (select 1 from RRL_TT_GLOBAL_MESS where ID = 1);

insert into RRL_TYPE_PALL (ID, NAME)
select 1, unistr('\0422\0415\0420\041C\041E\0411\041E\041A\0421') from dual where not exists (select 1 from RRL_TYPE_PALL where ID = 1);
insert into RRL_TYPE_PALL (ID, NAME)
select 2, unistr('\0420\041E\041B\041B-\041F\041E\041B\041A\0410') from dual where not exists (select 1 from RRL_TYPE_PALL where ID = 2);
insert into RRL_TYPE_PALL (ID, NAME)
select 3, unistr('\0420\041E\041B\041B') from dual where not exists (select 1 from RRL_TYPE_PALL where ID = 3);
insert into RRL_TYPE_PALL (ID, NAME)
select 4, unistr('\041E\0412\041E\0429\041D\041E\0419') from dual where not exists (select 1 from RRL_TYPE_PALL where ID = 4);
insert into RRL_TYPE_PALL (ID, NAME)
select 5, unistr('\041F\0410\041B\041B\0415\0422') from dual where not exists (select 1 from RRL_TYPE_PALL where ID = 5);

create or replace function RRL_DELETE_OP2(
  PUID1 varchar2,
  user_id1 varchar2
)
return varchar2
is
begin
  delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID = PUID1;
  delete from RRL_SBORKA_PALLETS where PALLET_UID = PUID1 and TRANSTASK_ID is null;
  if sql%rowcount > 0 then return 'ok'; end if;
  return '';
end RRL_DELETE_OP2;
/