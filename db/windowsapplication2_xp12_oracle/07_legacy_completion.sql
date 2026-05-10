prompt [07] Legacy completion patch for Oracle 19c compatibility
declare
  v_count number;
begin
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_WARES' and column_name = 'AUTO_PLAN_DOCK';
  if v_count = 0 then
    execute immediate 'alter table RRL_WARES add (AUTO_PLAN_DOCK NUMBER default 0)';
  end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_CELLS' and column_name = 'Y_VISOTA';
  if v_count = 0 then
    execute immediate 'alter table RRL_CELLS add (Y_VISOTA NUMBER)';
  end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_REVIZION' and column_name = 'REV_NAKLAD_ID';
  if v_count = 0 then
    execute immediate 'alter table RRL_REVIZION add (REV_NAKLAD_ID NUMBER)';
  end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_REVIZION' and column_name = 'SNAPSHOT_BEFORE';
  if v_count = 0 then
    execute immediate 'alter table RRL_REVIZION add (SNAPSHOT_BEFORE NUMBER)';
  end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_REVIZION' and column_name = 'SNAPSHOT_AFTER';
  if v_count = 0 then
    execute immediate 'alter table RRL_REVIZION add (SNAPSHOT_AFTER NUMBER)';
  end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_TRANSPORT_TYPE' and column_name = 'MIN_PALLET_LOAD';
  if v_count = 0 then
    execute immediate 'alter table RRL_TRANSPORT_TYPE add (MIN_PALLET_LOAD NUMBER default 0)';
  end if;
  select count(*) into v_count from user_tab_columns where table_name = 'RRL_SBORKA_PALLET_ROWS' and column_name = 'PRIHOD_PALLET_UID_COUNT';
  if v_count = 0 then
    execute immediate 'alter table RRL_SBORKA_PALLET_ROWS add (PRIHOD_PALLET_UID_COUNT NUMBER)';
  end if;
end;
/
declare
  v_count number;
begin
  select count(*) into v_count from user_tables where table_name = 'RRL_REMAIN_SNAPSHOT';
  if v_count = 0 then
    execute immediate q'[
      create table RRL_REMAIN_SNAPSHOT (
        ID             NUMBER not null,
        TYPE1          NUMBER not null,
        SNAP_SHOT_TIME DATE not null,
        CLOSED         NUMBER default 0,
        CREATE_TIME    DATE
      )
    ]';
    execute immediate 'alter table RRL_REMAIN_SNAPSHOT add constraint RRL_REMAIN_SNAPSHOT_PK primary key (ID)';
    execute immediate 'create index RRL_REMAIN_SNAPSHOT_I1 on RRL_REMAIN_SNAPSHOT (TYPE1, CLOSED)';
    execute immediate 'create index RRL_REMAIN_SNAPSHOT_I2 on RRL_REMAIN_SNAPSHOT (SNAP_SHOT_TIME, CREATE_TIME)';
  end if;
  select count(*) into v_count from user_tables where table_name = 'RRL_REMAIN_SNAPSHOT_ROWS';
  if v_count = 0 then
    execute immediate q'[
      create table RRL_REMAIN_SNAPSHOT_ROWS (
        ID           NUMBER not null,
        ARTICUL      VARCHAR2(50),
        PALLET_UID   VARCHAR2(150),
        CELL         VARCHAR2(50),
        WARE_ID      NUMBER,
        SNAP_TIME    DATE,
        REMAIN       NUMBER,
        CONDITION    NUMBER default 0,
        SNAP_SHOT_ID NUMBER
      )
    ]';
    execute immediate 'alter table RRL_REMAIN_SNAPSHOT_ROWS add constraint RRL_REMAIN_SNAPSHOT_ROWS_I1 primary key (ID)';
    execute immediate 'create index RRL_PEMAIN_SNAPSHOT_ROWS_I2 on RRL_REMAIN_SNAPSHOT_ROWS (ARTICUL, PALLET_UID, CELL, WARE_ID)';
    execute immediate 'create index RRL_REMAIN_SNAPSHOT_ROWS_I11 on RRL_REMAIN_SNAPSHOT_ROWS (SNAP_SHOT_ID)';
    execute immediate 'create index RRL_REMAIN_SNAPSHOT_ROWS_I9 on RRL_REMAIN_SNAPSHOT_ROWS (CONDITION)';
    execute immediate 'create index RRL_REMIAN_SNAPSHOT_ROWS_I5 on RRL_REMAIN_SNAPSHOT_ROWS (SNAP_TIME)';
  end if;
  select count(*) into v_count from user_sequences where sequence_name = 'RRL_REMAIN_SNAPSHOT_SQ';
  if v_count = 0 then
    execute immediate 'create sequence RRL_REMAIN_SNAPSHOT_SQ start with 1 increment by 1 nocache';
  end if;
  select count(*) into v_count from user_sequences where sequence_name = 'RRL_REMAIN_SNAPSHOT_ROWS_SQ';
  if v_count = 0 then
    execute immediate 'create sequence RRL_REMAIN_SNAPSHOT_ROWS_SQ start with 1 increment by 1 nocache';
  end if;
  select count(*) into v_count from user_triggers where trigger_name = 'RRL_REMAIN_SNAPSHOT_ROWS_TRG';
  if v_count = 0 then
    execute immediate q'[
      create or replace trigger RRL_REMAIN_SNAPSHOT_ROWS_TRG
      before insert on RRL_REMAIN_SNAPSHOT_ROWS
      for each row
      begin
        if :new.ID is null then
          select RRL_REMAIN_SNAPSHOT_ROWS_SQ.nextval into :new.ID from dual;
        end if;
      end;
    ]';
  end if;
end;
/
@legacy_extracts/07_remains_package.sql
@legacy_extracts/07_remains_package_body.sql
create or replace function RRL_SBORKA_PALLET_ROWS_ADD2 (
  PALLET_UID1    VARCHAR2,
  ARTICUL1       VARCHAR2,
  SHORTNAME1     VARCHAR2,
  SHTRIHKOD1     VARCHAR2,
  EI1            VARCHAR2,
  TAREWEIGHT1    NUMBER,
  PATH1          VARCHAR2,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2,
  ware_id1       int
) return int
is
  ID1 int;
begin
  select ID
    into ID1
    from RRL_SBORKA_PALLET_ROWS
   where PALLET_UID = PALLET_UID1
     and ARTICUL = ARTICUL1;
  return ID1;
exception
  when NO_DATA_FOUND then
    select RRL_SBORKA_PALLET_ROWS_SQ.Nextval into ID1 from DUAL;
    insert into RABAEV.RRL_SBORKA_PALLET_ROWS (
      ID,
      PALLET_UID,
      ARTICUL,
      SHORTNAME,
      SHTRIHKOD,
      EI,
      TAREWEIGHT,
      PATH,
      ORDER_WEIGHT,
      TARESIZE,
      QUANTITY,
      SORTFIELD,
      AUCTION,
      DOCID,
      ware_id
    ) values (
      ID1,
      PALLET_UID1,
      ARTICUL1,
      SHORTNAME1,
      SHTRIHKOD1,
      EI1,
      TAREWEIGHT1,
      PATH1,
      ORDER_WEIGHT1,
      TARESIZE1,
      QUANTITY1,
      SORTFIELD1,
      AUCTION1,
      DOCID1,
      ware_id1
    );
    return ID1;
end RRL_SBORKA_PALLET_ROWS_ADD2;
/
create or replace function RRL_TT_REORDER_ADR(IDTT int)
 return number
is
  tmpVar number;
  planned_at timestamp;
  cursor dddd is
    select ID, PALLET_UID, ADDR, rownum as ORD1
      from (
        select P.ID, P.PALLET_UID, P.ADDR, ADR.ORD
          from RABAEV.RRL_SBORKA_PALLETS P, RRL_ADDR ADR
         where TRANSTASK_ID = IDTT
           and P.ADDR = ADR.ADDR(+)
         order by ADR.ORD, P.PALLET_UID
      );
begin
  tmpVar := 0;
  for sss in dddd loop
    update RRL_SBORKA_PALLETS
       set ORD = sss.ORD1
     where ID = sss.ID;
  end loop;
  tmpVar := RRL_GET_TT_PRICE(IDTT);
  update RRL_TRANSPORT_TASK TT
     set PRICE = tmpVar
   where TT.ID = IDTT;
  planned_at := RRL_TT_PLAN_SHIPPPING_HOUR(IDTT);
  return tmpVar;
exception
  when NO_DATA_FOUND then
    return 0;
  when others then
    return 0;
end RRL_TT_REORDER_ADR;
/
create or replace function RRL_UPDATE_OTHOD_PALLET_ROWS2(
  PALLET_UID_to varchar,
  row_id_from int
) return int
is
  tmpVar int;
begin
  tmpVar := 0;
  return tmpVar;
end RRL_UPDATE_OTHOD_PALLET_ROWS2;
/
create or replace function RRL_OTHOD_PALLET_PODBOR_PARTII(
  PALLET_ID1 varchar2
) return varchar2
is
  tmpVar int;
  current_cell varchar2(50);
  kolvo_otbora number;
  PALLET_ROW_ID1 int;
  count_of_PUID int;
  new_part_id int;
  vychet number;
  all_found int;
  mod_id4 int;
  articul_for varchar2(255);
  cursor rowss is
    select *
      from RABAEV.RRL_SBORKA_PALLET_ROWS rs
     where PALLET_UID = PALLET_ID1
       and (
         PRIHOD_PALLET_UID is null or
         (
           REMAINS.remains_partion_in_otbor(rs.PRIHOD_PALLET_UID) <= 0 or
           (
             REMAINS.remains_partion_in_otbor(rs.PRIHOD_PALLET_UID) is null and
             REMAINS.REMAINS_EXCEPT_PART_IN_OTB(rs.PRIHOD_PALLET_UID) > 0
           )
         )
       );
  cursor rests_in_cell is
    select RABAEV.RRL_REMAINS.REMAIN,
           RABAEV.RRL_REMAINS.UID_POLETA,
           RRL_PALLETS.EXPIRY_DATE,
           RRL_PALLETS.ARTICUL
      from RABAEV.RRL_REMAINS, RABAEV.RRL_PALLETS
     where RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET
       and RRL_REMAINS.CELL = current_cell
       and RRL_REMAINS.REMAIN > 0
       and RRL_PALLETS.ARTICUL = articul_for
     order by RRL_PALLETS.EXPIRY_DATE;
begin
  all_found := 1;
  select condition into tmpVar
    from RABAEV.RRL_SBORKA_PALLETS
   where PALLET_UID = PALLET_ID1;
  if tmpVar >= 2 then
    return 'closed already';
  end if;
  count_of_PUID := 0;
  new_part_id := 0;
  for naklad_row in rowss loop
    count_of_PUID := 0;
    PALLET_ROW_ID1 := naklad_row.ID;
    tmpVar := 0;
    kolvo_otbora := naklad_row.QUANTITY;
    articul_for := naklad_row.ARTICUL;
    select CELL into current_cell
      from RABAEV.RRL_ARTICULS
     where ACTICUL = naklad_row.ARTICUL;
    for ddd8 in rests_in_cell loop
      if kolvo_otbora > 0 then
        count_of_PUID := count_of_PUID + 1;
        if kolvo_otbora <= ddd8.REMAIN then
          vychet := kolvo_otbora;
          kolvo_otbora := 0;
        else
          vychet := ddd8.REMAIN;
          kolvo_otbora := kolvo_otbora - ddd8.REMAIN;
        end if;
        if count_of_PUID = 1 then
          select PPP.MOD_ID into mod_id4
            from RRL_PALLETS PPP
           where PPP.UID_PALLET = ddd8.UID_POLETA;
          update RABAEV.RRL_SBORKA_PALLET_ROWS
             set CURRENT_MOD_ID = mod_id4,
                 PRIHOD_PALLET_UID = ddd8.UID_POLETA,
                 PRIHOD_PALLET_UID_COUNT = count_of_PUID,
                 EXPIRY_DATE = ddd8.EXPIRY_DATE
           where ID = naklad_row.ID;
          delete from RABAEV.RRL_SBORKA_PALL_ROWS_PARTS
           where PALLET_UID = ddd8.UID_POLETA
             and ARTICUL = ddd8.ARTICUL;
        else
          select RABAEV.RRL_SBORKA_PALL_ROWS_PARTSSQ.NEXTVAL into new_part_id from dual;
          insert into RABAEV.RRL_SBORKA_PALL_ROWS_PARTS (
            ID,
            PALLET_UID,
            COUNT,
            ARTICUL,
            EXPIRY_DATE
          ) values (
            new_part_id,
            ddd8.UID_POLETA,
            kolvo_otbora,
            ddd8.ARTICUL,
            ddd8.EXPIRY_DATE
          );
          update RABAEV.RRL_SBORKA_PALLET_ROWS
             set PRIHOD_PALLET_UID_COUNT = count_of_PUID
           where ID = naklad_row.ID;
        end if;
      end if;
    end loop;
  end loop;
  return 'ok';
exception
  when NO_DATA_FOUND then
    return 'NO_DATA_FOUND';
  when others then
    return 'ERROR';
end RRL_OTHOD_PALLET_PODBOR_PARTII;
/
alter package DOCK_PLANNING compile body;
alter package GOODS_TO_PICK compile body;
alter package REVIZION compile body;
alter package TRANSPORT_TASK compile body;
alter package REMAINS compile;
alter package REMAINS compile body;
begin
  dbms_utility.compile_schema(schema => user, compile_all => false);
end;
/
