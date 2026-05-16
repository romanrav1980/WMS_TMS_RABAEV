prompt [compat 2026-05-11] Windows client and Tserver API compatibility

declare
  procedure ensure_table_absent(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence_absent(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_sequences where sequence_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_column_absent(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate 'alter table ' || p_table || ' add (' || p_sql || ')';
    end if;
  end;
begin
  ensure_table_absent('RRL_SUPPLIERS',
    'create table RRL_SUPPLIERS (' ||
    'INN varchar2(50) not null, NAME varchar2(255) not null, SUPPLIER_GROUP varchar2(50), ' ||
    'constraint RRL_SUPPLIERS_PK primary key (INN))');

  ensure_table_absent('RRL_PALL_TRASH_REASON',
    'create table RRL_PALL_TRASH_REASON (' ||
    'ID number not null, NAME varchar2(255) not null, ' ||
    'constraint RRL_PALL_TRASH_REASON_PK primary key (ID))');

  ensure_table_absent('RRL_PALLETS_HIST',
    'create table RRL_PALLETS_HIST (' ||
    'ID number not null, PUID varchar2(50), TYPE varchar2(50), ' ||
    'DEF_PERC_BEFORE number, DEF_PERC_AFTRER number, DEF_PERC_REASON varchar2(255), EVENT_TIME date, ' ||
    'constraint RRL_PALLETS_HIST_PK primary key (ID))');

  ensure_table_absent('INVOICE_DH',
    'create table INVOICE_DH (' ||
    'ID number not null, DOC_NUMBER varchar2(100), DOC_DATE date, STATUS varchar2(50), CREATED_AT date default sysdate, ' ||
    'constraint INVOICE_DH_PK primary key (ID))');

  ensure_table_absent('RRL_TRP_MATRIX',
    'create table RRL_TRP_MATRIX (' ||
    'REG_F varchar2(250) not null, RAI_F varchar2(250) not null, REG_2 varchar2(250) not null, RAI_2 varchar2(250) not null, ' ||
    'DIST number default 0, TIME1 number default 0, ' ||
    'constraint RRL_TRP_MATRIX_PK primary key (REG_F, RAI_F, REG_2, RAI_2))');

  ensure_table_absent('RRL_TRP_ADDR_MATRIX',
    'create table RRL_TRP_ADDR_MATRIX (' ||
    'ADDR_FROM varchar2(255) not null, ADDR_TO varchar2(255) not null, DIST number default 0, TIME1 number default 0, ' ||
    'constraint RRL_TRP_ADDR_MATRIX_PK primary key (ADDR_FROM, ADDR_TO))');

  ensure_sequence_absent('RRL_PALLETS_HIST_SQ', 'create sequence RRL_PALLETS_HIST_SQ start with 1 increment by 1 nocache');

  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'PROOVED', 'PROOVED number default 0');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'DOCK', 'DOCK varchar2(50)');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'VECHILE_NUMBER', 'VECHILE_NUMBER varchar2(50)');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'VODITEL_NAME', 'VODITEL_NAME varchar2(255)');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'VODITEL_PHONE_NUMB', 'VODITEL_PHONE_NUMB varchar2(50)');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'CHECKING_TIME', 'CHECKING_TIME date');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'PRIORITY1', 'PRIORITY1 number default 10');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'PLANNING_ACCEPT_TIME', 'PLANNING_ACCEPT_TIME date');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'INVITE_TIME', 'INVITE_TIME date');
  ensure_column_absent('RRL_PRIHOD_NAKLAD', 'OHRANA_KPP', 'OHRANA_KPP varchar2(50)');

  ensure_column_absent('RRL_PALLETS', 'REASON_ID', 'REASON_ID number');
  ensure_column_absent('RRL_PALLETS', 'GTD', 'GTD varchar2(255)');
  ensure_column_absent('RRL_PALLETS', 'SERTIF', 'SERTIF varchar2(255)');

  ensure_column_absent('RRL_CELLS', 'PICK_ORDER', 'PICK_ORDER number default 0');
  ensure_column_absent('RRL_CELLS', 'LAST_USER_ID', 'LAST_USER_ID varchar2(50)');
  ensure_column_absent('RRL_CELLS', 'CELL_WEIGHT', 'CELL_WEIGHT number');
  ensure_column_absent('RRL_CELLS', 'CELL_HEIGHT', 'CELL_HEIGHT number');

  ensure_column_absent('RRL_TRANSPORT_TASK', 'MAIL_SENDED', 'MAIL_SENDED number default 0');
end;
/

merge into RRL_PALL_TRASH_REASON d
using (select 1 ID, 'DEFECT_PERCENT_CHANGE' NAME from dual) s
on (d.ID = s.ID)
when not matched then insert (ID, NAME) values (s.ID, s.NAME);

create or replace view RRL_TRP_REGIONS as
select region, min(ord) ord
  from RRL_ADDR
 where region is not null
 group by region;
/

create or replace package HELP is
  function update_object(
    OBJECT_NAME1 varchar2,
    BUSINESS_FIELD1 varchar2,
    PARENT_OBJECT1 varchar2,
    COMMENT11 varchar2,
    TYPE2 varchar2,
    ARTICLE2 varchar2
  ) return int;
end HELP;
/

create or replace package body HELP is
  function update_object(
    OBJECT_NAME1 varchar2,
    BUSINESS_FIELD1 varchar2,
    PARENT_OBJECT1 varchar2,
    COMMENT11 varchar2,
    TYPE2 varchar2,
    ARTICLE2 varchar2
  ) return int is
  begin
    merge into RRL_OBJECT d
    using (
      select OBJECT_NAME1 OBJECT_NAME, BUSINESS_FIELD1 BUSINESS_FIELD, PARENT_OBJECT1 PARENT_OBJECT,
             COMMENT11 COMMENT1, TYPE2 TYPE1, ARTICLE2 ARTICLE1
        from dual
    ) s
    on (d.OBJECT_NAME = s.OBJECT_NAME and nvl(d.PARENT_OBJECT, '#') = nvl(s.PARENT_OBJECT, '#'))
    when matched then update set
      d.BUSINESS_FIELD = s.BUSINESS_FIELD,
      d.COMMENT1 = s.COMMENT1,
      d.TYPE1 = s.TYPE1,
      d.ARTICLE1 = s.ARTICLE1
    when not matched then insert (OBJECT_NAME, BUSINESS_FIELD, PARENT_OBJECT, COMMENT1, TYPE1, ARTICLE1)
      values (s.OBJECT_NAME, s.BUSINESS_FIELD, s.PARENT_OBJECT, s.COMMENT1, s.TYPE1, s.ARTICLE1);

    return 1;
  exception
    when others then return 0;
  end;
end HELP;
/

create or replace package STORE_ADRESSES is
  function Update_cell(
    CELL1 varchar2,
    OTBOR1 integer,
    BLOCKED_FOR_REMAINS1 integer,
    BLOCKED_FOR_POPOLNENIE1 integer,
    X1 integer,
    Y1 integer,
    Z1 integer,
    BLOCKED_FOR_ACCEPT1 integer,
    WARE_ID1 integer,
    LIMIT_WEIGHT1 number,
    LIMIT_HEIGHT1 number,
    Y_VISOTA1 number,
    CELL_WEIGHT1 number,
    CELL_HEIGHT1 number,
    PICK_ORDER1 integer,
    LAST_USER_ID1 varchar2
  ) return int;
end STORE_ADRESSES;
/

create or replace package body STORE_ADRESSES is
  function Update_cell(
    CELL1 varchar2,
    OTBOR1 integer,
    BLOCKED_FOR_REMAINS1 integer,
    BLOCKED_FOR_POPOLNENIE1 integer,
    X1 integer,
    Y1 integer,
    Z1 integer,
    BLOCKED_FOR_ACCEPT1 integer,
    WARE_ID1 integer,
    LIMIT_WEIGHT1 number,
    LIMIT_HEIGHT1 number,
    Y_VISOTA1 number,
    CELL_WEIGHT1 number,
    CELL_HEIGHT1 number,
    PICK_ORDER1 integer,
    LAST_USER_ID1 varchar2
  ) return int is
  begin
    merge into RRL_CELLS d
    using (select CELL1 CELL from dual) s
    on (d.CELL = s.CELL)
    when matched then update set
      d.OTBOR = OTBOR1,
      d.BLOCKED_FOR_REMAINS = BLOCKED_FOR_REMAINS1,
      d.BLOCKED_FOR_POPOLNENIE = BLOCKED_FOR_POPOLNENIE1,
      d.X = X1,
      d.Y = Y1,
      d.Z = Z1,
      d.BLOCKED_FOR_ACCEPT = BLOCKED_FOR_ACCEPT1,
      d.WARE_ID = WARE_ID1,
      d.LIMIT_WEIGHT = LIMIT_WEIGHT1,
      d.LIMIT_HEIGHT = LIMIT_HEIGHT1,
      d.Y_VISOTA = Y_VISOTA1,
      d.CELL_WEIGHT = CELL_WEIGHT1,
      d.CELL_HEIGHT = CELL_HEIGHT1,
      d.PICK_ORDER = PICK_ORDER1,
      d.LAST_USER_ID = LAST_USER_ID1,
      d.LAST_TIME_OF_UPDATE = sysdate
    when not matched then insert (
      CELL, OTBOR, BLOCKED_FOR_REMAINS, BLOCKED_FOR_POPOLNENIE,
      X, Y, Z, BLOCKED_FOR_ACCEPT, WARE_ID, LIMIT_WEIGHT, LIMIT_HEIGHT, Y_VISOTA,
      CELL_WEIGHT, CELL_HEIGHT, PICK_ORDER, LAST_USER_ID, LAST_TIME_OF_UPDATE
    ) values (
      CELL1, OTBOR1, BLOCKED_FOR_REMAINS1, BLOCKED_FOR_POPOLNENIE1,
      X1, Y1, Z1, BLOCKED_FOR_ACCEPT1, WARE_ID1, LIMIT_WEIGHT1, LIMIT_HEIGHT1, Y_VISOTA1,
      CELL_WEIGHT1, CELL_HEIGHT1, PICK_ORDER1, LAST_USER_ID1, sysdate
    );

    return 1;
  exception
    when others then return 0;
  end;
end STORE_ADRESSES;
/

create or replace package PRIHOD is
  function prihod_is_closed(ord_id int) return int;
  function close_price_control(prih_id int) return int;
  function set_brak_perc_new(puid1 varchar2, new_perc number, reason_id int) return int;
  function set_dock(prih_id int, h_dock varchar2) return int;
  function set_ware_id(prih_id int, new_ware_id int) return int;
  function set_priority(prih_id int, new_priority_id int, new_user_id varchar2) return int;
  function set_prihod_kpp(prihod_id int, kpp_n varchar2) return int;
  function is_prihod_fresh(prihod_id int) return varchar2;
  function prihod_pall_count(prihod_naklad_id int) return int;
  function get_brak_reason(reason_id int) return varchar2;
  function order_zakaz_number(prihod_naklad_id int) return varchar2;
end PRIHOD;
/

create or replace package body PRIHOD is
  function prihod_is_closed(ord_id int) return int is
    cond1 number;
  begin
    select nvl(condition, 0) into cond1 from RRL_PRIHOD_NAKLAD where id = ord_id;
    if cond1 >= 2 then return 1; end if;
    return 0;
  exception
    when no_data_found then return -1;
  end;

  function close_price_control(prih_id int) return int is
    cond1 number;
    prooved1 number;
    vehicle1 varchar2(50);
  begin
    select nvl(condition, 0), nvl(prooved, 0), vechile_number
      into cond1, prooved1, vehicle1
      from RRL_PRIHOD_NAKLAD
     where id = prih_id;

    if cond1 >= 2 then return 3; end if;
    if prooved1 >= 1 then return 2; end if;
    if vehicle1 is null then return -4; end if;

    update RRL_PRIHOD_NAKLAD
       set prooved = 1,
           priority1 = nvl(priority1, 10),
           checking_time = nvl(checking_time, sysdate)
     where id = prih_id;
    return 1;
  exception
    when no_data_found then return -1;
  end;

  function set_brak_perc_new(puid1 varchar2, new_perc number, reason_id int) return int is
    old_perc number;
    reason_name varchar2(255);
    hist_id number;
  begin
    select nvl(defect_perc, 0) into old_perc from RRL_PALLETS where uid_pallet = puid1;
    begin
      select name into reason_name from RRL_PALL_TRASH_REASON where id = reason_id;
    exception
      when no_data_found then reason_name := to_char(reason_id);
    end;

    update RRL_PALLETS
       set defect_perc = new_perc,
           reason_id = reason_id
     where uid_pallet = puid1;

    select RRL_PALLETS_HIST_SQ.nextval into hist_id from dual;
    insert into RRL_PALLETS_HIST (ID, PUID, TYPE, DEF_PERC_BEFORE, DEF_PERC_AFTRER, DEF_PERC_REASON, EVENT_TIME)
    values (hist_id, puid1, 'DEFECT_PERCENT', old_perc, new_perc, reason_name, sysdate);

    return 1;
  exception
    when no_data_found then return -1;
    when others then return 0;
  end;

  function set_dock(prih_id int, h_dock varchar2) return int is
  begin
    update RRL_PRIHOD_NAKLAD
       set dock = h_dock,
           invite_time = nvl(invite_time, sysdate)
     where id = prih_id
       and nvl(condition, 0) < 2;
    if sql%rowcount = 0 then return 0; end if;
    return 1;
  end;

  function set_ware_id(prih_id int, new_ware_id int) return int is
  begin
    update RRL_PRIHOD_NAKLAD
       set ware_id = new_ware_id
     where id = prih_id
       and nvl(condition, 0) < 2;
    if sql%rowcount = 0 then return 0; end if;
    return 1;
  end;

  function set_priority(prih_id int, new_priority_id int, new_user_id varchar2) return int is
  begin
    update RRL_PRIHOD_NAKLAD
       set priority1 = new_priority_id
     where id = prih_id
       and nvl(condition, 0) < 2;
    if sql%rowcount = 0 then return 0; end if;
    return 1;
  end;

  function set_prihod_kpp(prihod_id int, kpp_n varchar2) return int is
  begin
    update RRL_PRIHOD_NAKLAD
       set ohrana_kpp = kpp_n,
           invite_time = sysdate
     where id = prihod_id
       and nvl(condition, 0) < 2;
    if sql%rowcount = 0 then return 0; end if;
    return 1;
  end;

  function is_prihod_fresh(prihod_id int) return varchar2 is
    invite1 date;
  begin
    select invite_time into invite1 from RRL_PRIHOD_NAKLAD where RRL_PRIHOD_NAKLAD.id = is_prihod_fresh.prihod_id;
    if invite1 is null then return '0'; end if;
    if invite1 >= sysdate - (10 / 1440) then
      return unistr('\0432\044B\0437\043E\0432');
    end if;
    return '1';
  exception
    when no_data_found then return '0';
  end;

  function prihod_pall_count(prihod_naklad_id int) return int is
    cnt int;
  begin
    select count(*) into cnt from RRL_PALLETS where PRIHOD_NAKLAD_ID = prihod_naklad_id;
    return cnt;
  end;

  function get_brak_reason(reason_id int) return varchar2 is
    reason_name varchar2(255);
  begin
    select name into reason_name from RRL_PALL_TRASH_REASON where id = reason_id;
    return reason_name;
  exception
    when no_data_found then return null;
  end;

  function order_zakaz_number(prihod_naklad_id int) return varchar2 is
    zakaz varchar2(255);
  begin
    select zakaz_number into zakaz from RRL_PRIHOD_NAKLAD where id = prihod_naklad_id;
    return zakaz;
  exception
    when no_data_found then return null;
  end;
end PRIHOD;
/

create or replace package PALL_SPLITTER is
  function show_sq_gr(articul1 varchar2, ware_id1 int) return int;
  function is_pallet_has_full_pallet_row(pallet_uid1 varchar2) return int;
  function add_row_2sborka_pallets(articul1 varchar2, count1 number, pall_uid1 varchar2, ware_id1 int, ord_number1 varchar2) return int;
  function create_return_task(supp_inn varchar2, user_id1 varchar2, ware_id1 int) return varchar2;
  function split_ufa(ord_number1 varchar2, ware_id2 int) return int;
  function split_vegetables(ord_number1 varchar2, ware_id2 int) return int;
end PALL_SPLITTER;
/

create or replace package body PALL_SPLITTER is
  function show_sq_gr(articul1 varchar2, ware_id1 int) return int is
  begin
    return COMPL.show_sq_gr(articul1, ware_id1);
  exception
    when others then return 101;
  end;

  function is_pallet_has_full_pallet_row(pallet_uid1 varchar2) return int is
    cnt int;
  begin
    select count(*) into cnt
      from RRL_SBORKA_PALLET_ROWS
     where pallet_uid = pallet_uid1
       and nvl(original_quantity, 0) > 0
       and nvl(quantity, 0) >= nvl(original_quantity, 0);
    if cnt > 0 then return 1; end if;
    return 0;
  end;

  function add_row_2sborka_pallets(articul1 varchar2, count1 number, pall_uid1 varchar2, ware_id1 int, ord_number1 varchar2) return int is
    row_id1 int;
  begin
    select RRL_SBORKA_PALLET_ROWS_SQ.nextval into row_id1 from dual;

    insert into RRL_SBORKA_PALLET_ROWS (
      ID, PALLET_UID, ARTICUL, SHORTNAME, SHTRIHKOD, EI,
      ORDER_WEIGHT, TARESIZE, QUANTITY, SORTFIELD, WARE_ID,
      PACK_COUNT, ORIGINAL_QUANTITY, ORIGINAL_ORDER_WEIGHT
    )
    select row_id1, pall_uid1, art.ACTICUL, art.NAME, art.BARCODE_SHT, art.UNIT_TYPE,
           0, 0, count1, 999999, ware_id1, 0, count1, 0
      from RRL_ARTICULS art
     where art.ACTICUL = articul1;

    return row_id1;
  exception
    when no_data_found then return 0;
    when others then return 0;
  end;

  function create_return_task(supp_inn varchar2, user_id1 varchar2, ware_id1 int) return varchar2 is
    st1 varchar2(50);
    puid1 varchar2(80);
    id1 number;
  begin
    st1 := 'RET_' || to_char(sysdate, 'YYYYMMDDHH24MISS');
    puid1 := st1 || '_1';
    select RRL_SBORKA_PALLETS_SQ.nextval into id1 from dual;

    insert into RRL_SBORKA_PALLETS (
      ID, ST_NUMBER, CREATE_DATE, WARE_ID, PALLET_NUMBER, PALLET_UID,
      ADDR, STATE, STDATE, USER_ID, RETURN_SUPPLIER_ID
    ) values (
      id1, st1, sysdate, ware_id1, 1, puid1,
      'RETURN_SUPPLIER', 'RETURN', sysdate, user_id1, supp_inn
    );

    return st1;
  exception
    when others then return null;
  end;

  function split_ufa(ord_number1 varchar2, ware_id2 int) return int is
  begin
    return 0;
  end;

  function split_vegetables(ord_number1 varchar2, ware_id2 int) return int is
  begin
    return 0;
  end;
end PALL_SPLITTER;
/

create or replace package TRANSPORT_PLN is
  function get_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int;
  function get_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int;
  function get_time_m(AddrFrom varchar2, AddrTo varchar2) return number;
  function get_dist_m(AddrFrom varchar2, AddrTo varchar2) return number;
  function set_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, time1 number) return int;
  function set_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, dist number) return int;
  function set_time_m(AddrFrom varchar2, AddrTo varchar2, time1 number) return int;
  function set_distance_m(AddrFrom varchar2, AddrTo varchar2, dist1 number) return int;
  function is_tt_just_out_go(tt_id int) return int;
  function upd_tt_perdiction(tt_id int) return int;
  function set_mail_sended(tt_id int) return int;
  function set_tt_closed(tt_id int) return int;
end TRANSPORT_PLN;
/

create or replace package body TRANSPORT_PLN is
  function get_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int is
    ret number;
  begin
    select nvl(time1, 0) into ret from RRL_TRP_MATRIX
     where REG_F = get_time.reg_f and RAI_F = get_time.rai_f and REG_2 = get_time.reg_2 and RAI_2 = get_time.rai_2;
    return ret;
  exception
    when no_data_found then return 0;
  end;

  function get_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2) return int is
    ret number;
  begin
    select nvl(dist, 0) into ret from RRL_TRP_MATRIX
     where REG_F = get_distance.reg_f and RAI_F = get_distance.rai_f and REG_2 = get_distance.reg_2 and RAI_2 = get_distance.rai_2;
    return ret;
  exception
    when no_data_found then return 0;
  end;

  function get_time_m(AddrFrom varchar2, AddrTo varchar2) return number is
    ret number;
  begin
    select nvl(time1, 0) into ret from RRL_TRP_ADDR_MATRIX
     where ADDR_FROM = get_time_m.AddrFrom and ADDR_TO = get_time_m.AddrTo;
    return ret;
  exception
    when no_data_found then return 0;
  end;

  function get_dist_m(AddrFrom varchar2, AddrTo varchar2) return number is
    ret number;
  begin
    select nvl(dist, 0) into ret from RRL_TRP_ADDR_MATRIX
     where ADDR_FROM = get_dist_m.AddrFrom and ADDR_TO = get_dist_m.AddrTo;
    return ret;
  exception
    when no_data_found then return 0;
  end;

  function set_time(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, time1 number) return int is
  begin
    merge into RRL_TRP_MATRIX d
    using (select reg_f REG_F, rai_f RAI_F, reg_2 REG_2, rai_2 RAI_2, time1 TIME1 from dual) s
    on (d.REG_F = s.REG_F and d.RAI_F = s.RAI_F and d.REG_2 = s.REG_2 and d.RAI_2 = s.RAI_2)
    when matched then update set d.TIME1 = s.TIME1
    when not matched then insert (REG_F, RAI_F, REG_2, RAI_2, TIME1) values (s.REG_F, s.RAI_F, s.REG_2, s.RAI_2, s.TIME1);
    return 1;
  end;

  function set_distance(reg_f varchar2, rai_f varchar2, reg_2 varchar2, rai_2 varchar2, dist number) return int is
  begin
    merge into RRL_TRP_MATRIX d
    using (select reg_f REG_F, rai_f RAI_F, reg_2 REG_2, rai_2 RAI_2, dist DIST from dual) s
    on (d.REG_F = s.REG_F and d.RAI_F = s.RAI_F and d.REG_2 = s.REG_2 and d.RAI_2 = s.RAI_2)
    when matched then update set d.DIST = s.DIST
    when not matched then insert (REG_F, RAI_F, REG_2, RAI_2, DIST) values (s.REG_F, s.RAI_F, s.REG_2, s.RAI_2, s.DIST);
    return 1;
  end;

  function set_time_m(AddrFrom varchar2, AddrTo varchar2, time1 number) return int is
  begin
    merge into RRL_TRP_ADDR_MATRIX d
    using (select AddrFrom ADDR_FROM, AddrTo ADDR_TO, time1 TIME1 from dual) s
    on (d.ADDR_FROM = s.ADDR_FROM and d.ADDR_TO = s.ADDR_TO)
    when matched then update set d.TIME1 = s.TIME1
    when not matched then insert (ADDR_FROM, ADDR_TO, TIME1) values (s.ADDR_FROM, s.ADDR_TO, s.TIME1);
    return 1;
  end;

  function set_distance_m(AddrFrom varchar2, AddrTo varchar2, dist1 number) return int is
  begin
    merge into RRL_TRP_ADDR_MATRIX d
    using (select AddrFrom ADDR_FROM, AddrTo ADDR_TO, dist1 DIST from dual) s
    on (d.ADDR_FROM = s.ADDR_FROM and d.ADDR_TO = s.ADDR_TO)
    when matched then update set d.DIST = s.DIST
    when not matched then insert (ADDR_FROM, ADDR_TO, DIST) values (s.ADDR_FROM, s.ADDR_TO, s.DIST);
    return 1;
  end;

  function is_tt_just_out_go(tt_id int) return int is
    cond1 varchar2(100);
  begin
    select condition into cond1 from RRL_TRANSPORT_TASK where id = tt_id;
    if cond1 = unistr('\0412\042B\041F\0423\0429\0415\041D') then return 1; end if;
    return 0;
  exception
    when no_data_found then return -1;
  end;

  function upd_tt_perdiction(tt_id int) return int is
  begin
    update RRL_TRANSPORT_TASK
       set planned_delivery_date = nvl(shipment_date, sysdate) + (nvl(hours, 0) / 24)
     where id = tt_id;
    if sql%rowcount = 0 then return 0; end if;
    return 1;
  end;

  function set_mail_sended(tt_id int) return int is
  begin
    update RRL_TRANSPORT_TASK set mail_sended = 1 where id = tt_id;
    if sql%rowcount = 0 then return 0; end if;
    return 1;
  end;

  function set_tt_closed(tt_id int) return int is
  begin
    update RRL_TRANSPORT_TASK
       set condition = unistr('\0412\042B\041F\0423\0429\0415\041D')
     where id = tt_id;
    if sql%rowcount = 0 then return 0; end if;
    return 1;
  end;
end TRANSPORT_PLN;
/
