prompt Applying transport task implementations missing for WindowsApplication2 xp12
set define off

begin
  execute immediate 'drop table RRL_TRANSPORT_TASK_HISTORY cascade constraints';
exception
  when others then
    if sqlcode != -942 then
      raise;
    end if;
end;
/

begin
  execute immediate 'drop sequence RRL_TRANSPORT_TASK_HISTORY_SQ';
exception
  when others then
    if sqlcode != -2289 then
      raise;
    end if;
end;
/

begin
  execute immediate 'drop table RRL_TR_VODITEL_EXT cascade constraints';
exception
  when others then
    if sqlcode != -942 then
      raise;
    end if;
end;
/

-- Route history objects are required by tt_time_of_otg/service_level_otg
create table RRL_TRANSPORT_TASK_HISTORY
(
  id            INTEGER not null,
  ttask_id      INTEGER,
  user_id       VARCHAR2(50),
  transtype     VARCHAR2(20),
  transport     VARCHAR2(50),
  routetype     VARCHAR2(100),
  shipment_time DATE,
  voditel_id    INTEGER,
  primechanie   VARCHAR2(1024),
  dock          VARCHAR2(50),
  shipment_date DATE,
  operation     VARCHAR2(20),
  event_time    TIMESTAMP(0),
  st_number     VARCHAR2(50)
);

alter table RRL_TRANSPORT_TASK_HISTORY
  add constraint RRL_TRANSPORT_TASK_HISTORY_PK primary key (ID);

create index RRL_TRANSPORT_TASK_HISTORY_I1 on RRL_TRANSPORT_TASK_HISTORY (TTASK_ID, USER_ID);

create index RRL_TRANSPORT_TASK_HISTORY_I8 on RRL_TRANSPORT_TASK_HISTORY (TRANSPORT, VODITEL_ID, OPERATION);

create sequence RRL_TRANSPORT_TASK_HISTORY_SQ
  minvalue 1
  maxvalue 999999999999999999999999999
  start with 1
  increment by 1
  cache 20;

-- Driver-specific extension because RRL_TR_VODITEL has no INN/tabel fields in this schema line.
create table RRL_TR_VODITEL_EXT
(
  vod_id    INTEGER not null,
  tabel_no  VARCHAR2(50),
  inn       VARCHAR2(20),
  last_upd  DATE default sysdate,
  user_id   VARCHAR2(50)
);

alter table RRL_TR_VODITEL_EXT
  add constraint RRL_TR_VODITEL_EXT_PK primary key (VOD_ID);

create or replace package TRANSPORT_TASK is
  function PRINT_PALLET_WEIGHT( PALLET_UID2 varchar2 ) return varchar2;
  function can_print( tt_id int, user_id1 varchar2 ) return varchar2;
  function pallet_count( tt_id int ) return number;
  function tt_wares( tt_id int ) return varchar2;
  function stoim_pall_sb( pall_uid1 varchar2 ) return number;
  function stoim_tt( tt_id int ) return number;
  function test1 return int;
  function TT_UNREADY_COUNT( IDTT int ) return number;
  function TT_READY_PERC( IDTT int ) return number;
  function tt_unready_wares( tt_id int ) return varchar2;
  function TT_VODITEL_TEL( VODITEL_ID1 int ) return varchar2;
  function TT_REORDER_ADR( IDTT int ) return number;
  function RRL_PALLETS_STR( ST_NUMBER1 varchar2 ) return varchar2;
  function RRL_TT_PALLETS_STR( IDTT int ) return varchar2;
  function TT_TIME_OF_OTG( IDTT int ) return date;
  function SERVICE_LEVEL_OTG( IDTT int ) return number;
  function VODITEL_GET_INN( VOD_ID int ) return varchar2;
  function VODITEL_GET_TABEL_NUMB( VOD_ID int ) return varchar2;
  function VODITEL_SET_TABEL_NUMB( vod_id int, tabel_numb1 varchar2, inn1 varchar2 ) return int;
end TRANSPORT_TASK;
/

create or replace package body TRANSPORT_TASK is

function PRINT_PALLET_WEIGHT( PALLET_UID2 varchar2 ) return varchar2 is
  ret number;
  ware_id1 int;
  count_kor1 int;
  count_rs int;
  articul1 varchar2(255);
  sum_q number;
begin
  select round(TRIAL_WEIGHT, 2), pts.ware_id
    into ret, ware_id1
    from rrl_sborka_pallets pts
   where pts.pallet_uid = PALLET_UID2;

  if ret > 0 then
    return to_char(ret);
  end if;

  if ware_id1 = 5 then
    select sum(rs.pack_count)
      into count_kor1
      from rrl_sborka_pallet_rows rs
     where rs.pallet_uid = PALLET_UID2;
    return to_char(count_kor1) || ' РєРѕСЂ.';
  end if;

  select count(rs.id), sum(rs.pack_count), sum(rs.quantity)
    into count_rs, count_kor1, sum_q
    from rrl_sborka_pallet_rows rs
   where rs.pallet_uid = PALLET_UID2;

  if count_rs = 1 then
    select rs.articul
      into articul1
      from rrl_sborka_pallet_rows rs
     where rs.pallet_uid = PALLET_UID2;
    if articul1 = 'РҐ0000012233' then
      return to_char(count_kor1) || ' РєРѕСЂ.';
    end if;
  end if;

  return to_char(ret);
exception
  when no_data_found then
    return '-';
end;

function can_print( tt_id int, user_id1 varchar2 ) return varchar2 is
  ml int;
  cnt_pt int;
begin
  select type1.min_pallet_load
    into ml
    from rrl_transport_task tt, rrl_tr_vehicle veh, rrl_transport_type type1
   where tt.id = tt_id
     and veh.num = tt.transport
     and veh.tr_type = type1.transporttype;

  select count(pts.pallet_uid)
    into cnt_pt
    from rrl_sborka_pallets pts
   where pts.transtask_id = tt_id;

  if cnt_pt < ml then
    if rrl_has_wright(user_id1, 'SEND_EMPTY_TRUCK') = 1 then
      return 'ok';
    end if;
    return 'РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅР°СЏ Р·Р°РіСЂСѓР·РєР° РјР°СЂС€СЂСѓС‚Р°: ' || to_char(cnt_pt) || ' < ' || to_char(ml);
  end if;

  return 'ok';
exception
  when no_data_found then
    return 'ok';
  when others then
    return 'ok';
end;

function pallet_count( tt_id int ) return number is
  tmp number;
begin
  select count(pts.id)
    into tmp
    from rrl_sborka_pallets pts
   where pts.transtask_id = tt_id;
  return tmp;
exception
  when no_data_found then
    return 0;
end;

function stoim_pall_sb( pall_uid1 varchar2 ) return number is
  price1 number;
  total1 number;
  stoim_of_current_row number;
  cursor ss is
    select * from rrl_sborka_pallet_rows rs where rs.pallet_uid = pall_uid1;
begin
  total1 := 0;
  for r in ss loop
    stoim_of_current_row := 0;
    if r.prihod_pallet_uid is not null then
      begin
        select pts.price into price1 from rrl_pallets pts where pts.uid_pallet = r.prihod_pallet_uid;
        stoim_of_current_row := r.quantity * price1;
      exception
        when no_data_found then
          null;
      end;
    end if;

    if stoim_of_current_row = 0 then
      begin
        select art.last_price into price1 from rrl_articuls art where art.acticul = r.articul;
        stoim_of_current_row := r.quantity * price1;
      exception
        when no_data_found then
          stoim_of_current_row := 1;
      end;
    end if;

    total1 := total1 + stoim_of_current_row;
  end loop;
  return total1;
end;

function stoim_tt( tt_id int ) return number is
  total1 number;
begin
  select sum(stoim_pall_sb(pts.pallet_uid))
    into total1
    from rrl_sborka_pallets pts
   where pts.transtask_id = tt_id;
  return total1;
end;

function tt_wares( tt_id int ) return varchar2 is
  tmp varchar2(1024);
  cursor sss is
    select distinct RRL_SKLADNAME_BY_ID(pts.ware_id) g
      from rrl_sborka_pallets pts
     where pts.transtask_id = tt_id;
begin
  tmp := '';
  for i in sss loop
    tmp := tmp || to_char(i.g) || ' ';
  end loop;
  return tmp;
exception
  when no_data_found then
    return '';
  when others then
    return tmp;
end;

function test1 return int is
  curr_pr number;
  cursor arts is select acticul from rrl_articuls;
begin
  for a in arts loop
    begin
      select price
        into curr_pr
        from (
          select pts.articul, pts.price
            from rrl_pallets pts
           where pts.articul = a.acticul
             and price > 0
           order by pts.creation_date desc
        )
       where rownum <= 1;
      update rrl_articuls set last_price = curr_pr where acticul = a.acticul;
    exception
      when no_data_found then
        null;
    end;
  end loop;
  return 1;
end;

function TT_READY_PERC( IDTT int ) return number is
  tmpVar number;
  itogo int;
  sobrano int;
begin
  tmpVar := 0;
  select count(ID) into itogo from RABAEV.RRL_SBORKA_PALLETS where TRANSTASK_ID = IDTT;
  select count(ID)
    into sobrano
    from RABAEV.RRL_SBORKA_PALLETS P
   where TRANSTASK_ID = IDTT
     and (P.prooved = 1 or P.prooved_by_scan = 1 or P.condition = 2);
  if itogo = 0 then
    return 0;
  end if;
  tmpVar := sobrano / itogo;
  return tmpVar;
exception
  when no_data_found then
    return -1;
end;

function TT_UNREADY_COUNT( IDTT int ) return number is
  tmpVar number;
  itogo int;
  sobrano int;
begin
  tmpVar := 0;
  select count(ID) into itogo from RABAEV.RRL_SBORKA_PALLETS where TRANSTASK_ID = IDTT;
  select count(ID)
    into sobrano
    from RABAEV.RRL_SBORKA_PALLETS P
   where TRANSTASK_ID = IDTT
     and (P.prooved = 1 or P.prooved_by_scan = 1 or P.condition = 2);
  tmpVar := itogo - sobrano;
  return tmpVar;
exception
  when no_data_found then
    return -1;
end;

function tt_unready_wares( tt_id int ) return varchar2 is
  tmp varchar2(1024);
  cursor sss is
    select RRL_SKLADNAME_BY_ID(pts.ware_id) g, count(pts.pallet_uid) cnt
      from rrl_sborka_pallets pts
     where pts.transtask_id = tt_id
       and not (prooved = 1 or prooved_by_scan = 1 or condition = 2)
     group by RRL_SKLADNAME_BY_ID(pts.ware_id);
begin
  tmp := '';
  for i in sss loop
    tmp := tmp || to_char(i.g) || '=[' || to_char(i.cnt) || '] ';
  end loop;
  return tmp;
exception
  when no_data_found then
    return '!';
  when others then
    return tmp;
end;

function TT_VODITEL_TEL( VODITEL_ID1 int ) return varchar2 is
  tmpVar varchar2(255);
begin
  select VV.Tel into tmpVar from RABAEV.RRL_TR_VODITEL VV where ID = VODITEL_ID1;
  return tmpVar;
exception
  when no_data_found then
    return '';
end;

function TT_REORDER_ADR( IDTT int ) return number is
begin
  return RABAEV.RRL_TT_REORDER_ADR(IDTT);
exception
  when no_data_found then
    return 0;
end TT_REORDER_ADR;

function RRL_PALLETS_STR( ST_NUMBER1 varchar2 ) return varchar2 is
  tmp varchar2(4000);
  cnt number;
begin
  tmp := '';
  for r in (
    select distinct pallet_number
      from rrl_sborka_pallets
     where st_number = ST_NUMBER1
       and pallet_number is not null
     order by pallet_number
  ) loop
    if length(tmp) > 0 then
      tmp := tmp || ',';
    end if;
    tmp := tmp || to_char(r.pallet_number);
  end loop;

  if tmp is not null and length(tmp) > 0 then
    return tmp;
  end if;

  select count(pallet_uid)
    into cnt
    from rrl_sborka_pallets
   where st_number = ST_NUMBER1;

  return to_char(cnt);
exception
  when no_data_found then
    return '';
end;

function RRL_TT_PALLETS_STR( IDTT int ) return varchar2 is
begin
  return to_char(RABAEV.RRL_TT_PALLETS(IDTT));
exception
  when no_data_found then
    return '0';
end;

function TT_TIME_OF_OTG( IDTT int ) return date is
  ret date;
begin
  select cast(max(h.event_time) as date)
    into ret
    from RRL_TRANSPORT_TASK_HISTORY h
   where h.ttask_id = IDTT
     and h.operation = 'VERIFY_SECURITY';
  return ret;
exception
  when no_data_found then
    return null;
end;

function SERVICE_LEVEL_OTG( IDTT int ) return number is
  fact_time date;
  plan_time date;
begin
  fact_time := TT_TIME_OF_OTG(IDTT);
  select shipment_time into plan_time from RRL_TRANSPORT_TASK where ID = IDTT;

  if fact_time is null or plan_time is null then
    return null;
  end if;

  return round((fact_time - plan_time) * 24 * 60);
exception
  when no_data_found then
    return null;
end;

function VODITEL_GET_INN( VOD_ID int ) return varchar2 is
  ret varchar2(20);
begin
  select inn into ret from RRL_TR_VODITEL_EXT where vod_id = VOD_ID;
  return ret;
exception
  when no_data_found then
    return '';
end;

function VODITEL_GET_TABEL_NUMB( VOD_ID int ) return varchar2 is
  ret varchar2(50);
begin
  select tabel_no into ret from RRL_TR_VODITEL_EXT where vod_id = VOD_ID;
  return ret;
exception
  when no_data_found then
    return '';
end;

function VODITEL_SET_TABEL_NUMB( vod_id int, tabel_numb1 varchar2, inn1 varchar2 ) return int is
  vod_exists int;
begin
  select count(*) into vod_exists from RRL_TR_VODITEL where ID = vod_id;
  if vod_exists = 0 then
    return -1;
  end if;

  merge into RRL_TR_VODITEL_EXT dst
  using (
    select vod_id as vod_id, tabel_numb1 as tabel_no, inn1 as inn from dual
  ) src
  on (dst.vod_id = src.vod_id)
  when matched then
    update set dst.tabel_no = src.tabel_no,
               dst.inn = src.inn,
               dst.last_upd = sysdate
  when not matched then
    insert (vod_id, tabel_no, inn, last_upd)
    values (src.vod_id, src.tabel_no, src.inn, sysdate);

  return 1;
exception
  when others then
    return -2;
end;

begin
  null;
end TRANSPORT_TASK;
/
