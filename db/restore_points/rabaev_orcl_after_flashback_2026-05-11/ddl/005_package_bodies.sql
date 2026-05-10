set define off
set sqlblanklines on

prompt PACKAGE_BODY ARTICULS

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."ARTICULS" is
  function ei(articul1 varchar2) return varchar2 is
    type_w1 int;
  begin
    select art.type_w into type_w1
      from rrl_articuls art
     where art.acticul = articul1;

    if type_w1 in (0, 7) then
      return 'С€С‚';
    elsif type_w1 in (8, 1, 6, 5, 2, 3) then
      return 'РєРі';
    else
      return 'С€С‚';
    end if;
  exception
    when no_data_found then
      return 'С€С‚';
  end;

  function UPDATE_MOD(
    ID1             INTEGER,
    ARTICUL1        VARCHAR2,
    NAME1           VARCHAR2,
    SHT_IN_KOR1     NUMBER,
    SHT_WEIGHT1     NUMBER,
    KARTON_WEIGHT1  NUMBER,
    DELETED1        INTEGER,
    SHK_SHT1        VARCHAR2,
    SHK_KOR1        VARCHAR2,
    X               NUMBER,
    Y               NUMBER,
    Z               NUMBER,
    BRT_KOR         NUMBER
  ) return int
  is
    BRT_KOR2 number;
    ID2 int;
  begin
    if BRT_KOR is null or BRT_KOR <= 0 then
      BRT_KOR2 := nvl(KARTON_WEIGHT1, 0) + nvl(SHT_WEIGHT1, 0) * nvl(SHT_IN_KOR1, 0);
    else
      BRT_KOR2 := BRT_KOR;
    end if;

    if ID1 > 0 then
      update RRL_ARTICUL_MODS
         set ARTICUL           = ARTICUL1,
             NAME              = NAME1,
             SHT_IN_KOR        = SHT_IN_KOR1,
             SHT_WEIGHT        = SHT_WEIGHT1,
             KARTON_WEIGHT     = KARTON_WEIGHT1,
             DELETED           = DELETED1,
             SHK_SHT           = SHK_SHT1,
             SHK_KOR           = SHK_KOR1,
             DIMK_X            = X,
             DIMK_Y            = Y,
             DIMK_Z            = Z,
             BRT_WEIGHT_OF_KOR = BRT_KOR2
       where ID = ID1;
      return ID1;
    end if;

    insert into RRL_ARTICUL_MODS (
      ID,
      ARTICUL,
      NAME,
      SHT_IN_KOR,
      SHT_WEIGHT,
      KARTON_WEIGHT,
      DELETED,
      SHK_SHT,
      SHK_KOR,
      DIMK_X,
      DIMK_Y,
      DIMK_Z,
      BRT_WEIGHT_OF_KOR
    ) values (
      MODS_SEQ.NEXTVAL,
      ARTICUL1,
      NAME1,
      SHT_IN_KOR1,
      SHT_WEIGHT1,
      KARTON_WEIGHT1,
      DELETED1,
      SHK_SHT1,
      SHK_KOR1,
      X,
      Y,
      Z,
      BRT_KOR2
    );

    select MODS_SEQ.currval into ID2 from dual;
    return ID2;
  end;

  function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int is
    new_event_id int;
  begin
    if new_cell is null or current_cell is null then
      return -1;
    end if;

    for rm1 in (
      select rm.remain, rm.uid_poleta
        from rrl_remains rm,
             rrl_pallets pts
       where rm.cell = current_cell
         and pts.uid_pallet = rm.uid_poleta
         and pts.articul = articul1
    ) loop
      select RRL_EVENT_ID_SQ.nextval into new_event_id from dual;
      insert into RRL_EVENTS (
        ID_EVENT,
        CELL_FROM,
        CELL_TO,
        DATE_EVENT,
        COUNT_EVENT,
        TYPE_EVENT,
        UID_POLETA,
        USER_ID
      ) values (
        new_event_id,
        current_cell,
        new_cell,
        systimestamp,
        rm1.remain,
        2,
        rm1.uid_poleta,
        iser_id1
      );
    end loop;

    return 1;
  end;

  function eans(art1 varchar2) return varchar2 is
    tmp1 varchar2(4000);
  begin
    begin
      select art.barcode_sht into tmp1
        from rrl_articuls art
       where art.acticul = art1;
    exception
      when no_data_found then
        tmp1 := null;
    end;

    for r in (
      select shk_sht
        from rrl_articul_mods
       where articul = art1
         and deleted = 0
         and shk_sht is not null
    ) loop
      if tmp1 is null then
        tmp1 := r.shk_sht;
      else
        tmp1 := tmp1 || ';' || r.shk_sht;
      end if;
    end loop;

    return tmp1;
  end;
end ARTICULS;
/

prompt PACKAGE_BODY COMPL

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."COMPL" is
  function update_seq(articul1 varchar2, ware_id1 int, SQ1 int, SQGROUP int) return int is
    d1 int;
  begin
    select SQ.SEQ into d1 from RRL_COMPL_SEQ SQ where SQ.ARTICUL = articul1 and SQ.WARE_ID = ware_id1;
    update RRL_COMPL_SEQ set SEQ = SQ1, SEQ_GROUP = SQGROUP where articul = articul1 and ware_id = ware_id1;
    return 1;
  exception
    when no_data_found then
      insert into RRL_COMPL_SEQ (ARTICUL, WARE_ID, SEQ, SEQ_GROUP) values (articul1, ware_id1, SQ1, SQGROUP);
      return 1;
  end;

  function show_sq(articul1 varchar2, ware_id1 int) return int is
    ret1 int;
  begin
    select SQ.SEQ into ret1 from RRL_COMPL_SEQ SQ where articul = articul1 and ware_id = ware_id1;
    return ret1;
  exception
    when no_data_found then return 101;
    when others then
      delete from RRL_COMPL_SEQ where articul = articul1 and ware_id = ware_id1 and rownum > 1;
      select SQ.SEQ into ret1 from RRL_COMPL_SEQ SQ where articul = articul1 and ware_id = ware_id1;
      return ret1;
  end;

  function show_sq_gr(articul1 varchar2, ware_id1 int) return int is
    ret1 int;
  begin
    select SQ.SEQ_GROUP into ret1 from RRL_COMPL_SEQ SQ where articul = articul1 and ware_id = ware_id1;
    return ret1;
  exception
    when no_data_found then return 101;
    when others then
      delete from RRL_COMPL_SEQ where articul = articul1 and ware_id = ware_id1 and rownum > 1;
      select SQ.SEQ_GROUP into ret1 from RRL_COMPL_SEQ SQ where articul = articul1 and ware_id = ware_id1;
      return ret1;
  end;

  function path(articul1 varchar2, sborka_pallet_uid varchar2) return varchar2 is
    ret1 varchar2(50);
  begin
    select cell into ret1 from RRL_ARTICULS where acticul = articul1;
    return ret1;
  exception
    when no_data_found then return 'NO_ART';
    when others then return 'ERR8';
  end;

  function divide_st_bypal(stn varchar2, ware_id1 int) return int is
  begin
    return 0;
  end;

  function create_order_from_spallets(st_numb varchar2, user_id1 varchar2) return int is
    create_date1 date;
    ware_id1 integer;
    addr1 varchar2(255);
    state1 varchar2(50);
    orddate1 date;
    ord_id int;
  begin
    select RRL_ORDERS_SQ.nextval into ord_id from dual;
    delete from RRL_ORDERS where ORD_NUMBER = st_numb;

    select PAL.CREATE_DATE, PAL.WARE_ID, PAL.ADDR, PAL.STATE, PAL.CREATE_DATE
      into create_date1, ware_id1, addr1, state1, orddate1
      from RRL_SBORKA_PALLETS PAL where PAL.ST_NUMBER = st_numb and rownum = 1;

    insert into RRL_ORDERS (ID, CREATE_DATE, WARE_ID, ADDR, STATE, ORDDATE, USER_ID, ORD_NUMBER, COND, ORD1)
    values (ord_id, create_date1, ware_id1, addr1, state1, orddate1, user_id1, st_numb, 0, 0);

    for s in (
      select RR.EI, max(RR.TARESIZE) TARESIZE, max(RR.TAREWEIGHT) TAREWEIGHT,
             sum(RR.ORIGINAL_ORDER_WEIGHT) ORIGINAL_ORDER_WEIGHT,
             sum(RR.ORIGINAL_QUANTITY) ORIGINAL_QUANTITY,
             sum(RR.PACK_COUNT) PACK_COUNT, sum(RR.QUANTITY) QUANTITY,
             sum(RR.ORDER_WEIGHT) ORDER_WEIGHT, RR.ARTICUL, RR.SORTFIELD,
             PAL.WARE_ID, RR.SHORTNAME
        from RRL_SBORKA_PALLET_ROWS RR, RRL_SBORKA_PALLETS PAL
       where RR.PALLET_UID = PAL.PALLET_UID and PAL.ST_NUMBER = st_numb
       group by RR.EI, RR.ARTICUL, RR.SORTFIELD, PAL.WARE_ID, RR.SHORTNAME
       order by RR.SORTFIELD
    ) loop
      insert into RRL_ORDER_ROWS (
        ID, ORDER_ID, ARTICUL, SHORTNAME, EI, ORDER_WEIGHT, QUANTITY,
        SORTFIELD, WARE_ID, PACK_COUNT, ORIGINAL_QUANTITY,
        ORIGINAL_ORDER_WEIGHT, CONDITION, TARESIZE, TAREWEIGHT, QUANTITY_PLANNED
      ) values (
        RRL_ORDER_ROWS_SQ.nextval, ord_id, s.ARTICUL, s.SHORTNAME, s.EI,
        s.ORDER_WEIGHT, s.QUANTITY, s.SORTFIELD, s.WARE_ID, s.PACK_COUNT,
        s.ORIGINAL_QUANTITY, s.ORIGINAL_ORDER_WEIGHT, 0, s.TARESIZE, s.TAREWEIGHT, 0
      );
    end loop;

    return ord_id;
  end;

  function orders_start_plan(ord_id1 int) return int is
    ord_state int;
  begin
    select ordd.cond into ord_state from rrl_orders ordd where ordd.id = ord_id1;
    if ord_state > 1 then return 2; end if;
    update rrl_orders set cond = 1 where id = ord_id1 and cond = 0;
    update rrl_order_rows set condition = 1 where order_id = ord_id1 and nvl(condition, 0) = 0;
    return 1;
  exception
    when no_data_found then return -1;
  end;

  function orders_create_vycherk(ord_id1 int) return int is
    ord_state int;
  begin
    select ordd.cond into ord_state from rrl_orders ordd where ordd.id = ord_id1;
    if ord_state <> 1 then return 2; end if;
    update rrl_orders set cond = 2 where id = ord_id1 and cond = 1;
    update rrl_order_rows set condition = 4 where order_id = ord_id1 and condition = 1;
    return 2;
  exception
    when no_data_found then return -1;
  end;

  function orders_check(ware_id6 int) return int is
  begin
    for fo in (
      select ords.id
        from RRL_ORDER_ROWS rs2, RRL_ORDERS ords
       where rs2.order_id = ords.id and rs2.ware_id = ware_id6 and nvl(ords.cond, 0) < 2
       group by ords.id
      having min(nvl(rs2.condition, 0)) > 1
    ) loop
      update RRL_ORDERS set cond = 2 where id = fo.id;
    end loop;
    return 1;
  end;

  function truncate_order_by_remains(ware_id6 int) return int is
    type qty_by_art_t is table of number index by varchar2(50);
    allocated qty_by_art_t;
    qty_avail number;
    qty_plan number;
    partion1 varchar2(250);
    mod_id1 number;
    expdate1 date;
  begin
    delete from RRL_COMPL_RESERVE where WARE_ID = ware_id6;

    update rrl_order_rows rs
       set rs.mod_id = null,
           rs.quantity_planned = 0,
           rs.partionplanned = null,
           rs.condition = case when nvl(rs.condition, 0) in (1, 2) then 1 else rs.condition end
     where exists (
       select 1 from rrl_orders ords
        where ords.id = rs.order_id and ords.ware_id = ware_id6 and nvl(ords.cond, 0) in (1, 2)
     );

    for r in (
      select rs.id, rs.order_id, rs.articul, nvl(rs.quantity, 0) as quantity
        from rrl_order_rows rs, rrl_orders ords
       where rs.order_id = ords.id and ords.ware_id = ware_id6
         and nvl(ords.cond, 0) in (1, 2) and nvl(rs.condition, 0) in (1, 2)
       order by nvl(ords.ord1, 0), ords.id, nvl(rs.sortfield, 0), rs.id
    ) loop
      if not allocated.exists(r.articul) then allocated(r.articul) := 0; end if;
      qty_avail := nvl(REMAINS.remains_free_all(r.articul), 0) - nvl(allocated(r.articul), 0);
      if qty_avail < 0 then qty_avail := 0; end if;
      qty_plan := least(nvl(r.quantity, 0), qty_avail);
      partion1 := null; mod_id1 := null; expdate1 := null;

      if qty_plan > 0 then
        begin
          select uid_poleta, mod_id, expiry_date
            into partion1, mod_id1, expdate1
            from (
              select rm.uid_poleta, p.mod_id, p.expiry_date
                from rrl_remains rm, rrl_cells c, rrl_pallets p
               where rm.cell = c.cell and rm.uid_poleta = p.uid_pallet
                 and c.ware_id = ware_id6 and nvl(c.blocked_for_remains, 0) = 0
                 and rm.remain > 0 and p.articul = r.articul
               order by p.expiry_date, rm.uid_poleta
            ) where rownum = 1;
        exception when no_data_found then null;
        end;

        update rrl_order_rows
           set quantity_planned = qty_plan, condition = 2,
               partionplanned = partion1, mod_id = mod_id1
         where id = r.id;

        insert into RRL_COMPL_RESERVE (
          ID, ARTICUL, PARTIONID, QTY, ORDERID, ORDERROWID,
          CONDITION, EXPDATE, MOD_ID, WARE_ID
        ) values (
          RRL_COMPL_RESERVE_SQ.nextval, r.articul, partion1, qty_plan,
          r.order_id, r.id, 0, expdate1, mod_id1, ware_id6
        );

        allocated(r.articul) := nvl(allocated(r.articul), 0) + qty_plan;
      end if;
    end loop;

    return orders_check(ware_id6);
  end;

  function debug_truncate_rem(articul1 varchar2, ware_id6 int) return number is
    ret1 number;
  begin
    select nvl(sum(rm.remain), 0)
      into ret1
      from rrl_remains rm, rrl_pallets pal, rrl_cells cel
     where rm.uid_poleta = pal.uid_pallet and rm.cell = cel.cell
       and cel.ware_id = ware_id6 and nvl(cel.blocked_for_remains, 0) = 0
       and pal.articul = articul1;
    return ret1;
  exception when no_data_found then return 0;
  end;

  function debug_truncate_reserv(articul1 varchar2, ware_id6 int) return number is
    ret1 number;
  begin
    select nvl(sum(qty), 0) into ret1 from RRL_COMPL_RESERVE where ARTICUL = articul1 and WARE_ID = ware_id6;
    return ret1;
  exception when no_data_found then return 0;
  end;

  function debug_truncate_orders(articul1 varchar2, ware_id6 int) return number is
    ret1 number;
  begin
    select nvl(sum(rs.quantity), 0)
      into ret1
      from rrl_order_rows rs, rrl_orders ords
     where rs.order_id = ords.id and ords.ware_id = ware_id6
       and rs.articul = articul1 and nvl(ords.cond, 0) in (1, 2)
       and nvl(rs.condition, 0) in (1, 2);
    return ret1;
  exception when no_data_found then return 0;
  end;

  function order_vycherk_count(order_id1 int) return int is ret int;
  begin
    select count(id) into ret from rrl_order_rows ors where ors.order_id = order_id1 and ors.condition in (1, 4);
    return ret;
  exception when no_data_found then return 0;
  end;

  function order_rows_count(order_id1 int) return int is ret int;
  begin
    select count(id) into ret from rrl_order_rows where order_id = order_id1;
    return ret;
  exception when no_data_found then return 0;
  end;

  function reset_2_first_status(order_id1 int) return int is
  begin
    update rrl_order_rows
       set partionplanned = null, mod_id = null, quantity_planned = 0, condition = 0
     where order_id = order_id1;
    update rrl_orders set cond = 0 where id = order_id1;
    delete from RRL_COMPL_RESERVE where ORDERID = order_id1;
    return 1;
  exception when no_data_found then return 0;
  end;

  function RRL_SBORKA_PAL_REMOVE_EMPTY(ST_NUMBER1 varchar2, USER_ID1 varchar2) return int is
  begin
    delete from RRL_SBORKA_PALLET_ROWS
     where nvl(quantity, 0) = 0
       and PALLET_UID in (select PALLET_UID from rrl_sborka_pallets where st_number = ST_NUMBER1);

    delete from rrl_sborka_pallets pts
     where pts.st_number = ST_NUMBER1
       and not exists (select 1 from RRL_SBORKA_PALLET_ROWS rs where rs.PALLET_UID = pts.PALLET_UID);
    return 1;
  end;

  function RRL_GIVE_PALLET_UID(ST_NUMBER1 varchar2, USER_ID1 varchar2, PALLET_NUMBER1 int) return varchar2 is
    tmpV varchar2(255);
    ADDR1 varchar2(255);
    PALLET_UID1 varchar2(100);
    STATE1 varchar2(100);
    STDATE1 date;
    ware_id1 int;
    NAPR1 varchar2(255);
    TRANSTASK_ID1 int;
    id2 int;
  begin
    begin
      select pts.pallet_uid, pts.addr, pts.state, pts.STDATE, pts.Napr, pts.ware_id, pts.TRANSTASK_ID
        into PALLET_UID1, ADDR1, STATE1, STDATE1, NAPR1, ware_id1, TRANSTASK_ID1
        from rrl_sborka_pallets pts
       where pts.st_number = st_number1 and pts.pallet_number = PALLET_NUMBER1 and rownum = 1;
      return PALLET_UID1;
    exception when no_data_found then null;
    end;

    select pts.addr, pts.state, pts.STDATE, pts.Napr, pts.ware_id, pts.TRANSTASK_ID
      into ADDR1, STATE1, STDATE1, NAPR1, ware_id1, TRANSTASK_ID1
      from rrl_sborka_pallets pts where pts.st_number = st_number1 and rownum = 1;

    PALLET_UID1 := 'OP_' || ST_NUMBER1 || '_' || PALLET_NUMBER1;

    begin
      select pts.pallet_uid into tmpV from rrl_sborka_pallets pts where pts.pallet_uid = PALLET_UID1 and rownum = 1;
    exception when no_data_found then
      id2 := RRL_SBORKA_PALLETS_ADD2(ST_NUMBER1, ADDR1, PALLET_NUMBER1, PALLET_UID1, STATE1, STDATE1, NAPR1, USER_ID1, ware_id1);
    end;

    update rrl_sborka_pallets set TRANSTASK_ID = TRANSTASK_ID1 where pallet_uid = PALLET_UID1;
    return PALLET_UID1;
  exception when no_data_found then return 'error';
  end;

  function RRL_COPY_PALLET_ROW3(row_id2 int, count1 number, PALLET_UID_NEW VARCHAR2) return int is
    ID1 int;
    row1 RRL_SBORKA_PALLET_ROWS%rowtype;
  begin
    if count1 <= 0 then return 0; end if;
    select * into row1 from RRL_SBORKA_PALLET_ROWS where ID = row_id2;
    select RRL_SBORKA_PALLET_ROWS_SQ.nextval into ID1 from dual;

    insert into RRL_SBORKA_PALLET_ROWS (
      ID, PALLET_UID, ARTICUL, SHORTNAME, SHTRIHKOD, EI, TAREWEIGHT, PATH,
      ORDER_WEIGHT, TARESIZE, QUANTITY, SORTFIELD, AUCTION, DOCID, WARE_ID,
      PACK_COUNT, ORIGINAL_QUANTITY, ORIGINAL_ORDER_WEIGHT, CURRENT_MOD_ID,
      PRIHOD_PALLET_UID, EXPIRY_DATE
    ) values (
      ID1, PALLET_UID_NEW, row1.ARTICUL, row1.SHORTNAME, row1.SHTRIHKOD, row1.EI,
      row1.TAREWEIGHT, row1.PATH,
      case when nvl(row1.ORIGINAL_QUANTITY, 0) = 0 then row1.ORDER_WEIGHT else count1 * row1.ORIGINAL_ORDER_WEIGHT / row1.ORIGINAL_QUANTITY end,
      row1.TARESIZE, count1, row1.SORTFIELD, row1.AUCTION, row1.DOCID, row1.WARE_ID,
      row1.PACK_COUNT, row1.ORIGINAL_QUANTITY, row1.ORIGINAL_ORDER_WEIGHT,
      row1.CURRENT_MOD_ID, row1.PRIHOD_PALLET_UID, row1.EXPIRY_DATE
    );

    return ID1;
  exception when no_data_found then return 0;
  end;

  function SET_SBORSHIK(PALLET_UID1 varchar2, SBORSHIK1 varchar2, user_id1 varchar2) return int is
  begin
    return RRL_SET_SBORSHIK(PALLET_UID1, SBORSHIK1);
  exception when others then return 0;
  end;

  function pallet_compl_date(pall_uid varchar2) return date is
    check_time date;
    create_time date;
  begin
    select pts.create_date, pts.checking_time into create_time, check_time from rrl_sborka_pallets pts where pts.pallet_uid = pall_uid;
    if check_time is null then return create_time; end if;
    return check_time;
  exception when no_data_found then return null;
  end;

  function time_shift_start(time1 date) return date is
    curr_time date; h int;
  begin
    curr_time := time1; h := to_number(to_char(curr_time, 'HH24'));
    if h between 0 and 8 then
      curr_time := curr_time - 1;
      return to_date(to_char(curr_time, 'dd.mm.yyyy') || ' 20:00:00', 'dd.mm.yyyy hh24:mi:ss');
    elsif h between 8 and 20 then
      return to_date(to_char(curr_time, 'dd.mm.yyyy') || ' 08:00:00', 'dd.mm.yyyy hh24:mi:ss');
    else
      return to_date(to_char(curr_time, 'dd.mm.yyyy') || ' 20:00:00', 'dd.mm.yyyy hh24:mi:ss');
    end if;
  end;

  function time_shift_end(time1 date) return date is
    curr_time date; h int;
  begin
    curr_time := time1; h := to_number(to_char(curr_time, 'HH24'));
    if h between 0 and 8 then
      return to_date(to_char(curr_time, 'dd.mm.yyyy') || ' 08:00:00', 'dd.mm.yyyy hh24:mi:ss');
    elsif h >= 8 and h < 20 then
      return to_date(to_char(curr_time, 'dd.mm.yyyy') || ' 20:00:00', 'dd.mm.yyyy hh24:mi:ss');
    else
      curr_time := curr_time + 1;
      return to_date(to_char(curr_time, 'dd.mm.yyyy') || ' 08:00:00', 'dd.mm.yyyy hh24:mi:ss');
    end if;
  end;
end COMPL;
/

prompt PACKAGE_BODY CROSS_DOCKING

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."CROSS_DOCKING" is
  function SYNC_ARTICUL(articul1 varchar2) return int is
    cnt int;
  begin
    select count(*) into cnt from rrl_articuls where acticul = articul1;
    if cnt > 0 then return 1; else return 0; end if;
  end;

  function SYNC_MOD(mod_id1 int) return int is
    cnt int;
  begin
    select count(*) into cnt from rrl_articul_mods where id = mod_id1 and nvl(deleted, 0) = 0;
    if cnt > 0 then return 1; else return 0; end if;
  end;

  function SYNC_SBOR_PALL_ROW(row_id1 int) return int is
    cnt int;
  begin
    select count(*) into cnt from rrl_sborka_pallet_rows where id = row_id1;
    if cnt > 0 then return 1; else return 0; end if;
  end;

  function SYNC_SBORKA_PALL(sb_pall_uid varchar2) return int is
    v_condition number;
    v_prooved number;
    v_scan number;
    v_synced number;
  begin
    select nvl(condition, 0), nvl(prooved, 0), nvl(prooved_by_scan, 0), nvl(kross_syncronized, 0)
      into v_condition, v_prooved, v_scan, v_synced
      from rrl_sborka_pallets
     where pallet_uid = sb_pall_uid;

    if v_condition <> 2 and v_prooved <> 1 and v_scan <> 1 then
      return -1;
    end if;

    if v_synced = 1 then
      return 1;
    end if;

    update rrl_sborka_pallets set kross_syncronized = 1 where pallet_uid = sb_pall_uid;
    return 2;
  exception
    when no_data_found then return -3;
    when others then return -3;
  end;
end CROSS_DOCKING;
/

prompt PACKAGE_BODY DOCK_PLANNING

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."DOCK_PLANNING" is

 
  function IS_AUTO_PLAN_DOCK(  TT_ID int) return int is
      AUTO_PLAN_DOCK1 int;   
  begin

    select max( WR.AUTO_PLAN_DOCK ) AUTO_PLAN_DOCK into AUTO_PLAN_DOCK1 from RRL_SBORKA_PALLETS PAL , RRL_WARES WR
    where PAL.Transtask_Id=TT_ID and WR.ID=ware_id ;
           return AUTO_PLAN_DOCK1;

  exception when no_data_found then return 0;
     when others then return 0; 
  end;

begin
 null;
end DOCK_PLANNING;
/

prompt PACKAGE_BODY GOODS_TO_PICK

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."GOODS_TO_PICK" is

function add_summary_task( ware_id1 int ) return int
is
begin
    select RRL_SUMMARY_PICK_LIST_SQ.Nextval into id1 from dual;
    insert into  RABAEV.RRL_SUMMARY_PICK_LIST 
    (ID ,CREATEDATE , CONDITION , ware_id) 
    values  
    ( id1  , systimestamp  , 0 , ware_id1 );
return id1;
end;



-- СОЗДАНИЕ СУММАРНОГО СБОРОЧНОГО ЛИСТА 
function add_pallet_2_summary_task(  PUID varchar2 , summary_task_id1 int ) return int
is
tmp1 int;
begin
   select condition into tmp1 from  RABAEV.RRL_SUMMARY_PICK_LIST 
   where id=summary_task_id1 and condition=0;
   update  RABAEV.RRL_SBORKA_PALLETS  set summary_task_id  = summary_task_id1 
   where PALLET_UID=PUID and summary_task_id  is null;
 return 1;
 exception when no_data_found then return 0;
end;

-- СОЗДАНИЕ СУММАРНОГО СБОРОЧНОГО ЛИСТА 
function add_pallet_2_summary_task2(  PUID varchar2  ) return int
is
tmp1 int;
wid1 int;
summary_task_id1 int;
begin

   select ware_id into wid1 from   RRL_SBORKA_PALLETS PAL where PAL.PALLET_UID = PUID;
   summary_task_id1:= get_opened_summary_task( wid1 );

   select condition into tmp1 from  RABAEV.RRL_SUMMARY_PICK_LIST 
   where id=summary_task_id1 and condition=0;
   update  RABAEV.RRL_SBORKA_PALLETS  set summary_task_id  = summary_task_id1 
   where PALLET_UID=PUID and summary_task_id  is null;

   select PAL.SUMMARY_TASK_ID into summary_task_id1 from RRL_SBORKA_PALLETS PAL where PAL.PALLET_UID = PUID ;
   return summary_task_id1;

 exception when no_data_found then return 0;
end;


 -- ПОЛУЧИТЬ ПЕРВЫЙ СОЗДАННЫЙ И НЕЗАВЕРШЕННЫЙ СУММАРНЫЙ СБОРОЧНЫЙ ЛИСТ 
function get_opened_summary_task(ware_id1 int) return int
is
begin

    begin 
        select  max(ID) into id1 from RABAEV.RRL_SUMMARY_PICK_LIST 
        where condition=0 and ware_id=ware_id1 order by CREATEDATE desc  ;
        if(id1 is null) then
               return add_summary_task( ware_id1  );
        end if;
        return id1;
    exception 
        when no_data_found then  return add_summary_task( ware_id1  );
        when others then  return add_summary_task( ware_id1  );
    end ;
    return add_summary_task( ware_id1  );
end;

-- МЕРА БЛИЗОСТИ ПРИ ПОДБОРЕ ПАЛЛЕТЫ В ХРАНЕНИИ
-- Паллеты выбираются в порядке Срока годности и Близости к месту сборки.
-- Близость к месту сборки = Мера. =  x +z*100.
function distance_2_pick( CELL1 varchar2 , ware_id1 int ) return number is
x1 number  ;
y1 number ;
z1 number;
Y_VISOTA1 number;
begin
   select x,y,z , Y_VISOTA into x1,y1,z1 , Y_VISOTA1 from RRL_CELLS CL 
          where CELL=CELL1 and CL.WARE_ID=ware_id1;
  if(Y_VISOTA1 is null) then 
               Y_VISOTA1:=y1;
  end if;

  if z1 is null then z1:=0;
  end if; 
return x1+Y_VISOTA1*10+Z1;
 exception 
  when no_data_found then  return 100;
    when others then return 100;
end;


function update_wt_row( summary_task_id1 int , 
       articul1 varchar2 , QUANTITY1 number , QUANTITY_PLANNED1 number ,
       QUANTITY_COMPLETE1 number  ) return int 
is
cond1 int;
id1 int;
begin
    select id into id1 from RRL_SUMMARY_PICK_LIST_ROWS where ARTICUL = articul1 and SPL_ID = summary_task_id1;
    update RRL_SUMMARY_PICK_LIST_ROWS set 
           QUANTITY= QUANTITY1, QUANTITY_COMPLETE=QUANTITY_COMPLETE1 , 
           QUANTITY_PLANNED=QUANTITY_PLANNED1 , condition=cond1
    where
           ARTICUL = articul1 and SPL_ID = summary_task_id1;

  return id1;
exception
  when no_data_found then   
  begin
    insert into RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
    (ARTICUL , SPL_ID , QUANTITY , QUANTITY_COMPLETE , QUANTITY_PLANNED , CONDITION )
     values ( articul1 , summary_task_id1 , QUANTITY1 , QUANTITY_COMPLETE1 , QUANTITY_PLANNED1  ,  cond1 );
    return 1;
  end;
  when others then   
  begin

    delete from RABAEV.RRL_SUMMARY_PICK_LIST_ROWS where ARTICUL = articul1 and SPL_ID = summary_task_id1;  
    insert into RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
    (ARTICUL , SPL_ID , QUANTITY , QUANTITY_COMPLETE , QUANTITY_PLANNED , CONDITION )
     values ( articul1 , summary_task_id1 , QUANTITY1 , QUANTITY_COMPLETE1 , QUANTITY_PLANNED1  ,  cond1 );
    return 1;

  end;    

end update_wt_row;



-- СОЗДАТЬ ЗАДАЧИ ДЛЯ ВОДИТЕЛЕЙ   РИЧТРАКА 
/* на основании номера ССЛ (Суммарного сборочного листа) выбираем 
строки паллет, привязанных к этому ССЛ. 
Артикулы упорядочиваем в порядке сборки
*/

function delete_wtasks( summary_task_id1 int ) return int is
begin

delete from RABAEV.RRL_SUMMARY_PICK_LIST where ID = summary_task_id1;
return 0;
end;

function create_wtasks( summary_task_id1 int ) return int is
   ware_id2 int;
   articul3 varchar2(50);
   skolko_nado number;
   count2 number;
   tmp1 int ;

   flag_last_pal1 int;
   flag_partial1 int;
   cell_otb varchar2(50);
skolko_pologeno number;

-- КУРСОР СУММАРНЫЙ ЛИСТ .       
  cursor sss is
  select ARTICUL , Q , SEQ , SEQ_GROUP from (
  select ARTICUL , Q , compl.show_sq(ARTICUL , ware_id2) SEQ , 
   compl.show_sq_gr(ARTICUL , ware_id2) SEQ_GROUP
   from (
       select RS.ARTICUL , sum( RS.QUANTITY ) Q 
       from RABAEV.RRL_SBORKA_PALLETS PAL , 
       RABAEV.RRL_SBORKA_PALLET_ROWS RS , RRL_ARTICULS ART
       where PAL.SUMMARY_TASK_ID = summary_task_id1 and
       PAL.PALLET_UID=RS.PALLET_UID and RS.QUANTITY >0
       and ART.ACTICUL = RS.ARTICUL and ART.CELL='E-6-6-6-6'
        group by RS.ARTICUL
       ) )
   order by SEQ_GROUP ,SEQ 
   ; -- order by порядок сборки 


-- КУРСОР С ОСТАТКАМИ НА СКЛАДЕ ВО ВСЕХ ДОСТУПНЫХ ЯЧЕЙКАХ  
  cursor ostat is
  select RM.REMAIN , RM.CELL , RM.UID_POLETA , 
  distance_2_pick(RM.CELL , ware_id2 ) dist  , PL.EXPIRY_DATE
    from RRL_REMAINS RM , RRL_CELLS CL , RRL_PALLETS PL 
    where CL.WARE_ID=ware_id2 and RM.CELL=CL.CELL
   and CL.BLOCKED_FOR_POPOLNENIE=0 and CL.BLOCKED_FOR_REMAINS=0
   and PL.UID_PALLET=RM.UID_POLETA and PL.ARTICUL=articul3 and RM.REMAIN>0
  order by EXPIRY_DATE , dist  ; -- КУРСОР С ОСТАТКАМИ НА СКЛАДЕ ВО ВСЕХ ДОСТУПНЫХ ЯЧЕЙКАХ   



begin
  cell_otb:='';
  DBMS_OUTPUT.put_line( 'Начало create_wtasks ');
select condition , WARE_ID into tmp , ware_id2 
       from RABAEV.RRL_SUMMARY_PICK_LIST where id=summary_task_id1;

    if(tmp<>0) then
     return 0;    
    end if;
update RABAEV.RRL_SUMMARY_PICK_LIST set condition =1 where id=summary_task_id1; 
delete from RABAEV.RRL_WT where parent_id = summary_task_id1 and type1='WR1';

    for ss in sss loop -- По всем строкам ссумарного сборочного листа (ССЛ)
        -- DBMS_OUTPUT.put_line(  ss.ARTICUL ); 
         articul3:= ss.ARTICUL ; 
         cell_otb:='';
         begin
                    select CELL into cell_otb from rrl_articuls where acticul= articul3;
         exception
           when no_data_found then cell_otb:='NO';
         end;
         skolko_nado := ss.q;
         skolko_pologeno:=0;
         -- для каждой строки Артикул, количество подбираем 
         -- необходимое количество товара на паллетах в Хранении
         --    Берем его как максимально подходящий по срокам, наиболее близко-стоящий
         for ost1 in ostat loop

              flag_last_pal1 :=0;
              flag_partial1  :=0;

         if(skolko_nado>0) then
                  count2 :=  min2 ( ost1.Remain , skolko_nado );
                  -- если ost1.Remain > skolko_nado ставим метку последнего неполного паллета 
                  if  ost1.Remain > skolko_nado then 
                       flag_partial1:=1;
                  end if;

                  skolko_nado:= skolko_nado - count2 ;
                  DBMS_OUTPUT.put_line( 
                   concat( concat( concat( concat( ' ARTICUL=' , ss.ARTICUL )  ,
                   concat( ' CELL =' , ost1.CELL ) ) , concat(  ' dist=' , to_char(ost1.dist) ) ) ,
                   concat (concat( ' UID_POLETA =' , ost1.UID_POLETA ) ,
                   concat( ' EXPIRY_DATE =' , to_char( ost1.EXPIRY_DATE ) ) )   
                   ) ) ;
                   -- ДОБАВЛЯЕМ ДАННЫЙ ПАЛЛЕТ НА СПУСК ВНИЗ. 

                  -- если  skolko_nado=0 ставим метку последнего паллета
                  if(skolko_nado=0) then
                  flag_last_pal1 :=1;
                  end if;

                  insert into RABAEV.RRL_WT
                  (  
                  ORDER1 , 
                  articul ,
                    TYPE1 , --{ WR – Задача ричтраку на пополнение WR1 – Задача ричтраку на пополнение зоны динамического подбора }
                    PUID  , FROM1 , TO1   , COUNT1 ,   
                    --PLAN_START_TIME ,PLAN_END_TIME , FACT_START_TIME ,FACT_END_TIME ,
                    WORKER  , -- РИЧТРАК 
                    CONDTION   ,  -- Состояние. 0-не назначена 1-назначена 2-начата 3-закончена.
                    PARENT_ID , -- Ссылка на создателя.  summary_task_id
                    flag_partial ,
                    flag_last_pal
                  ) values ( 
                  ss.seq ,
                  articul3 ,
                  'WR1' ,  ost1.UID_POLETA  , ost1.cell , cell_otb , count2 , 
                  --null , null ,null , null 
                  null , 0 , summary_task_id1 , flag_partial1 , flag_last_pal1 );
                  skolko_pologeno := skolko_pologeno +count2;






                  -- КОНЕЦ СОЗДАНИЯ WTASK.
         end if;
         end loop;

         -- НЕ ХВАТАЕТ 
         if( skolko_nado>0 ) then
          DBMS_OUTPUT.put_line( concat( concat( 'для артикула ' , ss.articul ) , concat( ' не хватает ' ,  skolko_nado ) ) );

          insert into RABAEV.RRL_WT
                  (  
                  ORDER1 , 
                  articul ,
                    TYPE1 , --{ WR – Задача ричтраку на пополнение WR1 – Задача ричтраку на пополнение зоны динамического подбора }
                    PUID  , FROM1 , TO1   , COUNT1 ,   

                    WORKER  , -- РИЧТРАК 
                    CONDTION   ,  -- Состояние. 0-не назначена 1-назначена 2-начата 3-закончена.
                    PARENT_ID , -- Ссылка на создателя.  summary_task_id
                    flag_last_pal
                  ) values ( 
                  ss.seq ,
                  articul3 ,
                  'WR1' ,  'NULL'  , 'INVENT' , cell_otb , skolko_nado ,  
                  null , 0 , summary_task_id1 , 1 );

         end if;
         -- НЕ ХВАТАЕТ 


         tmp1:=update_wt_row( summary_task_id1  , 
                        ss.articul  , ss.q ,  skolko_pologeno ,
                        0  );

    end loop;
--    Закрываем ССЛ (condition=1)
     DBMS_OUTPUT.put_line( 'Конец create_wtasks ');
    update  RABAEV.RRL_SUMMARY_PICK_LIST  set condition=2 where id=summary_task_id1;
return 1;
end ;

-- Функции стратегии размещения товара по ячейкам. 

begin
  -- Initialization
 null;
end GOODS_TO_PICK;
/

prompt PACKAGE_BODY ORDERS

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."ORDERS" is
  function ei_by_type_w(type_w int) return varchar2 is
  begin
    if type_w in (0, 7) then return 'Р РЋРІвЂљВ¬Р РЋРІР‚С™';
    elsif type_w in (8, 1, 6, 5, 2, 3) then return 'Р В РЎвЂќР В РЎвЂ“';
    else return 'Р РЋРІвЂљВ¬Р РЋРІР‚С™'; end if;
  end;

  function wares_of_order(ord_number1 varchar2) return varchar2 is
    res varchar2(4000);
  begin
    res := null;
    for w in (
      select distinct cl.ware_id as ware_id
        from rrl_orders rd, rrl_order_rows rws, rrl_articuls art, rrl_cells cl
       where rws.order_id = rd.id and rd.ord_number = ord_number1
         and art.acticul = rws.articul and art.cell = cl.cell
         and nvl(rws.quantity_planned, 0) > 0
    ) loop
      if res is null then res := to_char(w.ware_id); else res := res || ' , ' || to_char(w.ware_id); end if;
    end loop;
    return nvl(res, '0');
  end;

  function contains_invalid_logo(ord_number1 varchar2) return int is
    res int;
  begin
    select count(rws.id) into res
      from rrl_orders rd, rrl_order_rows rws
     where rws.order_id = rd.id and rd.ord_number = ord_number1
       and nvl(rws.quantity_planned, 0) > 0
       and (obj2number(rws.tareweight) = 0 or obj2number(rws.taresize) = 0);
    return res;
  exception when no_data_found then return 0;
  end;

  function count_of_sq_gr(ord_number1 varchar2) return int is
    res int; ord_id int; ware_id2 int;
  begin
    select ords.ware_id, ords.id into ware_id2, ord_id from rrl_orders ords where ords.ord_number = ord_number1;
    select count(distinct COMPL.show_sq_gr(RS.ARTICUL, ware_id2)) into res
      from RRL_ORDER_ROWS RS where RS.ORDER_ID = ord_id and nvl(RS.QUANTITY_PLANNED, 0) > 0;
    return res;
  exception when no_data_found then return 0; when others then return 0;
  end;

  function cleanup_order2(ord_number1 varchar2) return int is
    cond1 int; ord_id int;
  begin
    select nvl(ords.cond, 0), ords.id into cond1, ord_id from rrl_orders ords where ords.ord_number = ord_number1;
    if cond1 > 4 then return 0; end if;
    delete from rrl_order_rows where order_id = ord_id;
    delete from rrl_orders where id = ord_id;
    delete from RRL_COMPL_RESERVE where ORDERID = ord_id;
    commit;
    return 1;
  exception when no_data_found then return -1;
  end;

  function cleanup_order(ord_id int) return int is cond1 int;
  begin
    select nvl(ords.cond, 0) into cond1 from rrl_orders ords where id = ord_id;
    if cond1 > 0 then return 0; end if;
    delete from rrl_order_rows where order_id = ord_id;
    delete from rrl_orders where id = ord_id;
    delete from RRL_COMPL_RESERVE where ORDERID = ord_id;
    return 1;
  exception when no_data_found then return -1;
  end;

  function DELETE_PALLETS(ST_NUMBER1 varchar2, user_id1 varchar2) return varchar2 is
  begin
    for roww in (
      select PALLET_UID from RRL_SBORKA_PALLETS where ST_NUMBER like ST_NUMBER1 || '%' and TRANSTASK_ID is null
    ) loop
      update rrl_sborka_pallets set user_id_last_upd = user_id1 where pallet_uid = roww.PALLET_UID;
      delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID = roww.PALLET_UID;
      delete from RRL_SBORKA_PALLETS where PALLET_UID = roww.PALLET_UID;
    end loop;
    return 'ok';
  exception when no_data_found then return null;
  end;

  function create_order(
    st_numb1 varchar2,
    CREATE_DATE1 date,
    WARE_ID1 integer,
    ADDR1 varchar2,
    STATE1 varchar2,
    ORDDATE1 date,
    user_id1 varchar2
  ) return int is ord_id int;
  begin
    begin
      select id into ord_id from rrl_orders where ord_number = st_numb1;
      return ord_id;
    exception when no_data_found then null;
    end;
    select RRL_ORDERS_SQ.nextval into ord_id from dual;
    insert into RRL_ORDERS (ID, CREATE_DATE, WARE_ID, ADDR, STATE, ORDDATE, USER_ID, ORD_NUMBER, COND, ORD1)
    values (ord_id, CREATE_DATE1, WARE_ID1, ADDR1, STATE1, ORDDATE1, user_id1, st_numb1, 0, 0);
    return ord_id;
  end;

  function add_order_row(ord_id int, ARTICUL1 varchar2, QUANTITY1 number, WARE_ID1 int) return int is
    SHORTNAME2 varchar2(255); EI2 varchar2(255); ORDER_WEIGHT2 number; SORTFIELD2 int;
    PACK_COUNT2 number; TARESIZE2 number; TAREWEIGHT2 number; new_QUANTITY1 number;
  begin
    select round((QUANTITY1 / nullif(art.count_sht_in_kor, 0)), nvl(art.round_to, 0)) * art.count_sht_in_kor
      into new_QUANTITY1
      from rrl_articuls art where art.acticul = ARTICUL1;

    select (new_QUANTITY1 / nullif(art.count_sht_in_kor, 0)),
           art.brutto_weight_of_kor,
           art.dimkor_x * art.dimkor_y * art.dimkor_z,
           (new_QUANTITY1 / nullif(art.count_sht_in_kor, 0)) * art.brutto_weight_of_kor,
           art.name, case when art.type_w in (0, 7) then 'С€С‚' when art.type_w in (8, 1, 6, 5, 2, 3) then 'РєРі' else 'С€С‚' end
      into PACK_COUNT2, TAREWEIGHT2, TARESIZE2, ORDER_WEIGHT2, SHORTNAME2, EI2
      from rrl_articuls art where art.acticul = ARTICUL1;

    SORTFIELD2 := COMPL.show_sq(ARTICUL1, WARE_ID1);

    insert into RRL_ORDER_ROWS (
      ID, ORDER_ID, ARTICUL, SHORTNAME, EI, ORDER_WEIGHT, QUANTITY, SORTFIELD,
      WARE_ID, PACK_COUNT, ORIGINAL_QUANTITY, ORIGINAL_ORDER_WEIGHT, CONDITION,
      TARESIZE, TAREWEIGHT, MOD_ID, QUANTITY_PLANNED, PARTIONPLANNED
    ) values (
      RRL_ORDER_ROWS_SQ.nextval, ord_id, ARTICUL1, SHORTNAME2, EI2, ORDER_WEIGHT2,
      new_QUANTITY1, SORTFIELD2, WARE_ID1, PACK_COUNT2, QUANTITY1, ORDER_WEIGHT2,
      0, TARESIZE2, TAREWEIGHT2, 0, 0, null
    );

    if TARESIZE2 is null then return 2;
    elsif TAREWEIGHT2 is null then return 3;
    else return 1; end if;
  exception when no_data_found then return -1;
  end;

  function get_unfinished_quantity(articul1 varchar2, from_date1 date) return number is ret1 number;
  begin
    select nvl(sum(nvl(rs.quantity_planned, 0)), 0) into ret1
      from rrl_order_rows rs, rrl_orders ords
     where rs.order_id = ords.id and rs.articul = articul1
       and nvl(ords.create_date, ords.orddate) >= from_date1
       and nvl(ords.cond, 0) in (1, 2, 3, 4, 5)
       and nvl(rs.condition, 0) in (1, 2, 3, 4);
    return ret1;
  exception when no_data_found then return 0;
  end;

  function get_unfinished_quantityo(articul1 varchar2, from_date1 date) return number is ret1 number;
  begin
    select nvl(sum(nvl(rs.quantity, 0)), 0) into ret1
      from rrl_order_rows rs, rrl_orders ords
     where rs.order_id = ords.id and rs.articul = articul1
       and nvl(ords.create_date, ords.orddate) >= from_date1
       and nvl(ords.cond, 0) in (0, 1, 2, 3, 4, 5)
       and nvl(rs.condition, 0) in (0, 1, 2, 3, 4);
    return ret1;
  exception when no_data_found then return 0;
  end;
end ORDERS;
/

prompt PACKAGE_BODY PK_PIVOT

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."PK_PIVOT" pk_pivot
as
  procedure formatparam(var_data in varchar2, var_type in number, out_decode in out varchar2, out_col in out varchar2);


  function pivotsql(p_query in varchar2, p_rowfields in varchar2, p_columnfield in varchar2, p_function in varchar2, p_functionfield in varchar2
, p_page in number default 1 )
    return varchar2
  as
    l_max_cols        number;
    l_query           long;
    l_columnnames     array_varchar2 := array_varchar2();
    l_cursor          refcursor;
    tmp               long;
    --dbms_sql types:
    l_thecursor       integer default dbms_sql.open_cursor ;                                                                           --get col types
    l_colcnt          number default 0 ;
    l_desctbl         dbms_sql.desc_tab;
    col_num           number;
    l_columnfieldtype number;
    --decode names
    o_decode          varchar2(50);
    o_col             varchar2(50);
    l_cols_per_page   number := 50;
    l_begcol          number;
    l_endcol          number;
  begin
    --check params
    if instr(p_columnfield, ',') > 0
    then
      raise_application_error(-20001, 'Can use only 1 columnfield');
    elsif upper(p_function) not in ('SUM', 'AVG', 'COUNT', 'MIN', 'MAX')
    then
      raise_application_error(-20001, 'Can use only standard aggregate functions');
    end if;


    /* analyse query */
    dbms_sql.parse(l_thecursor, p_query, dbms_sql.native);
    /* get described columns for analysed query */
    dbms_sql.describe_columns(l_thecursor, l_colcnt, l_desctbl);

    /* Tom Kyte:
    * Following loop could simply be for j in 1..col_cnt loop.


    Here we are simply illustrating some of the PL/SQL table
    features.
    */
    col_num := l_desctbl.first;

    loop
      exit when (col_num is null);

      --find column field type
      if l_desctbl(col_num).col_name = upper(p_columnfield)
      then
        l_columnfieldtype := l_desctbl(col_num).col_type;
      --dbms_output.put_line('Col#:'||col_num||' Name:'||l_descTbl(col_num).col_name||' Type:'||l_descTbl(col_num).col_type);
      end if;

      col_num := l_desctbl.next(col_num);
    end loop;

    --return 'test ok';

    -- figure out the column names we must support for horizontal cross
    if (p_columnfield is not null)
    then
      tmp :=
           'SELECT DISTINCT '
        || p_columnfield
        || ' FROM ('
        || p_query
        || ') ORDER BY '
        || p_columnfield;

      -- dbms_output.put_line('columns cursor:'||tmp);
      open l_cursor for tmp;

      loop
        l_columnnames.extend;

        fetch l_cursor into l_columnnames(l_columnnames.count);

        --dbms_output.put_line('l_columnnames:'||l_columnnames(l_columnnames.COUNT));
        exit when l_cursor%notfound;
      end loop;

      close l_cursor;
    -- execute immediate 'SELECT DISTINCT ' || p_columnfield || ' FROM (' || p_query || ')' bulk collect into l_columnnames ;

    else
      raise_application_error(-20001, 'Cannot figure out max cols');
    end if;

    -- Now, construct the query that can answer the question for us...
    l_query :=
      'SELECT '
      || p_rowfields;


    l_begcol :=
      l_cols_per_page
      * (p_page
         - 1)
      + 1;
    l_endcol :=
      l_cols_per_page
      * p_page;


    if l_begcol > l_columnnames.count
                  - 1
    then
      l_begcol :=
        l_columnnames.count
        - 1;
    end if;


    if l_endcol > l_columnnames.count
                  - 1
    then
      l_endcol :=
        l_columnnames.count
        - 1;
    end if;


    --for i in 1 .. l_columnnames.count-1 loop
    for i in l_begcol .. l_endcol
    loop
      formatparam(l_columnnames(i), l_columnfieldtype, o_decode, o_col);                                                               --format params
      l_query :=
           l_query
        || ','
        || p_function
        || '(DECODE('
        || p_columnfield
        || ','
        || o_decode
        || ','
        || p_functionfield
        || ',null)) as "'
        || o_col
        || '" ';                                                                                                             --" РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…
    end loop;

    l_query :=
         l_query
      || ' FROM ('
      || p_query
      || ')';


    l_query :=
         l_query
      || ' GROUP BY '
      || p_rowfields
      || ' ORDER BY '
      || p_rowfields;


    /* close cursor */
    dbms_sql.close_cursor(l_thecursor);


    return l_query;
  exception
    when others
    then
      /* close cursor */
      dbms_sql.close_cursor(l_thecursor);
      raise_application_error(-20001, 'Error in PivotSQL:'
                                      || sqlerrm);
  end;

  --=========================


  procedure formatparam(var_data in varchar2, var_type in number, out_decode in out varchar2, out_col in out varchar2)
  --format parameter based on its type - for PivotSQL
  --get parameter and its type
  -- return strings for decode function and column name
  /* dbms_sql.describe_columns types:
  DATE Type:12
  Varchar2 Type:1
  Number Type:2
  */
  is
  begin
    if var_data is null
    then
      out_decode := 'NULL';
      out_col := '==NULL==';
    elsif var_type = 1
    then                                                                                                                                   -- Varchar2
      out_decode :=
           ''''
        || var_data
        || '''';                                                                                                                          --add quotes
      out_col := substr(var_data, 1, 30);
    elsif var_type = 2
    then                                                                                                                                      --Number
      out_decode := var_data;                                                                                                             --do nothing
      out_col := substr(var_data, 1, 30);
    elsif var_type = 12
    then                                                                                                                                        --DATE
      out_decode :=
           'to_date('''
        || var_data
        || ''')';                                                                                                            --format as internal date
      out_col := to_char(to_date(var_data), 'YYYY-MM-DD');
    else
      out_decode :=
        '== UNDEFINED TYPE:'
        || var_type;
      out_col := '== UNDEFINED TYPE';
    end if;
  exception
    when others
    then
      raise_application_error(-20001, 'Error in FormatParam:'
                                      || sqlerrm);
  end;
end;
/

prompt PACKAGE_BODY REMAINS

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."REMAINS" is
  function create_snapshot(type2 int) return int is
    id1 int;
  begin
    select RRL_REMAIN_SNAPSHOT_SQ.nextval into id1 from dual;
    insert into RRL_REMAIN_SNAPSHOT (ID, TYPE1, CREATE_TIME, SNAP_SHOT_TIME, CLOSED)
    values (id1, type2, systimestamp, systimestamp, 0);
    return id1;
  end;
  function add_row_2_snapshot(snap_shot_id1 int, cell1 varchar, articul1 varchar2) return int is
    tmp int;
    ware_id1 int;
    id1 int;
    snap_time1 date;
    cursor sss is
      select rm.uid_poleta, rm.remain
        from rrl_remains rm
        join rrl_pallets pts on pts.uid_pallet = rm.uid_poleta
       where rm.cell = cell1
         and pts.articul = articul1;
  begin
    if cell1 is null or articul1 is null then
      return -1;
    end if;
    select closed, snap_shot_time into tmp, snap_time1
      from RRL_REMAIN_SNAPSHOT where ID = snap_shot_id1;
    if tmp = 1 then
      return -1;
    end if;
    begin
      select ID into id1 from RRL_REMAIN_SNAPSHOT_ROWS
       where ARTICUL = articul1 and CELL = cell1 and SNAP_SHOT_ID = snap_shot_id1;
      return id1;
    exception when no_data_found then null;
    end;
    select ware_id into ware_id1 from rrl_cells where cell = cell1;
    for s in sss loop
      select RRL_REMAIN_SNAPSHOT_ROWS_SQ.nextval into id1 from dual;
      insert into RRL_REMAIN_SNAPSHOT_ROWS (ID, ARTICUL, CELL, PALLET_UID, REMAIN, WARE_ID, CONDITION, SNAP_SHOT_ID, SNAP_TIME)
      values (id1, articul1, cell1, s.uid_poleta, s.remain, ware_id1, 0, snap_shot_id1, snap_time1);
    end loop;
    return 1;
  exception
    when no_data_found then return -2;
  end;
  function close_snapshot(snap_shot_id1 int) return int is
    time_shot date;
  begin
    time_shot := systimestamp;
    update RRL_REMAIN_SNAPSHOT set CLOSED = 1, SNAP_SHOT_TIME = time_shot where ID = snap_shot_id1;
    return 1;
  end;
  function remains_free(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rem.remain), 0) into tmp
      from rrl_remains rem
      join rrl_cells cel on rem.cell = cel.cell
      join rrl_pallets pts on rem.uid_poleta = pts.uid_pallet
     where cel.blocked_for_remains = 0
       and pts.articul = articul1
       and rem.remain > 0
       and nvl(cel.otbor, 0) = 0;
    return tmp;
  exception when others then return 0; end;
  function remains_in_otbor(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rem.remain), 0) into tmp
      from rrl_remains rem
      join rrl_cells cel on rem.cell = cel.cell
      join rrl_pallets pts on rem.uid_poleta = pts.uid_pallet
     where pts.articul = articul1
       and rem.remain > 0
       and nvl(cel.otbor, 0) = 1;
    return tmp;
  exception when others then return 0; end;
  function remains_in_otbor_all(articul1 varchar2) return number is
  begin
    return remains_in_otbor(articul1);
  end;
  function remains_free_all(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rem.remain), 0) into tmp
      from rrl_remains rem
      join rrl_pallets pts on rem.uid_poleta = pts.uid_pallet
     where pts.articul = articul1
       and rem.remain > 0;
    return tmp;
  exception when others then return 0; end;
  function remains_partion_in_cell(pallet_uid1 varchar2, cell3 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(remain), 0) into tmp
      from rrl_remains
     where uid_poleta = pallet_uid1
       and cell = cell3
       and remain > 0;
    return tmp;
  exception when others then return 0; end;
  function remains_partion_in_otbor(pallet_uid1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rm.remain), 0) into tmp
      from rrl_remains rm
      join rrl_cells cl on rm.cell = cl.cell
     where rm.uid_poleta = pallet_uid1
       and rm.remain > 0
       and nvl(cl.otbor, 0) = 1;
    return tmp;
  exception when others then return 0; end;
  function remains_except_part_in_otb(pallet_uid1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rm.remain), 0) into tmp
      from rrl_remains rm
      join rrl_cells cl on rm.cell = cl.cell
      join rrl_pallets p on rm.uid_poleta = p.uid_pallet
      join rrl_pallets src on src.uid_pallet = pallet_uid1
     where p.articul = src.articul
       and rm.uid_poleta <> pallet_uid1
       and rm.remain > 0
       and nvl(cl.otbor, 0) = 1;
    return tmp;
  exception when others then return 0; end;
  function close_othod_pallet(PALLET_ID1 varchar2, iser_id21 varchar2) return varchar2 is
  begin
    return RRL_CLOSE_OTHOD_PALLET(PALLET_ID1, iser_id21);
  end;
  function trial_by_weight(PALLET_UID1 varchar2, TRIAL_WEIGHT1 varchar2, WOOD_WEIGHT1 varchar2, user_id1 varchar2) return int is
  begin
    return RRL_TRIAL_BY_WEIGHT(PALLET_UID1, TRIAL_WEIGHT1, WOOD_WEIGHT1, user_id1);
  end;
  function set_scan_proove(PALLET_UID1 varchar2, count_of_errors1 int, prim1 varchar2, SBORSHIK1 varchar2, KLADOVSHIK1 varchar2) return int is
  begin
    return RRL_SET_SCAN_PROOVE2(PALLET_UID1, count_of_errors1, prim1, SBORSHIK1, KLADOVSHIK1);
  end;
  function OTHOD_PALLET_PODBOR_PARTI4CELL(PALLET_ID1 varchar2, cell1 varchar2) return int is
    tmpVar int;
    current_cell varchar2(50);
    kolvo_otbora number;
    count_of_PUID int;
    mod_id4 int;
    articul_for varchar2(255);
    cursor rowss is
      select * from RRL_SBORKA_PALLET_ROWS rs where rs.PALLET_UID = PALLET_ID1;
    cursor rests_in_cell is
      select rm.remain, rm.uid_poleta, p.expiry_date, p.articul
        from rrl_remains rm join rrl_pallets p on rm.uid_poleta = p.uid_pallet
       where rm.cell = current_cell and rm.remain > 0 and p.articul = articul_for
       order by p.expiry_date;
  begin
    select condition into tmpVar from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_ID1;
    if tmpVar >= 2 then return -1; end if;
    for naklad_row in rowss loop
      count_of_PUID := 0;
      kolvo_otbora := naklad_row.quantity;
      articul_for := naklad_row.articul;
      current_cell := cell1;
      for ddd8 in rests_in_cell loop
        exit when kolvo_otbora <= 0;
        count_of_PUID := count_of_PUID + 1;
        select PPP.MOD_ID into mod_id4 from RRL_PALLETS PPP where PPP.UID_PALLET = ddd8.UID_POLETA;
        update RRL_SBORKA_PALLET_ROWS
           set CURRENT_MOD_ID = mod_id4,
               PRIHOD_PALLET_UID = ddd8.UID_POLETA,
               PRIHOD_PALLET_UID_COUNT = count_of_PUID,
               EXPIRY_DATE = ddd8.EXPIRY_DATE
         where ID = naklad_row.ID;
        kolvo_otbora := 0;
      end loop;
    end loop;
    return 1;
  exception when no_data_found then return 0; end;
  function othod_pallet_podbor_partii(PALLET_ID1 varchar2) return int is
    return_supplier_id1 varchar2(255);
    tmpVar int;
    current_cell varchar2(50);
    kolvo_otbora number;
    count_of_PUID int;
    mod_id4 int;
    articul_for varchar2(255);
    cursor rowss is
      select * from RRL_SBORKA_PALLET_ROWS rs
       where rs.PALLET_UID = PALLET_ID1
         and (
           rs.PRIHOD_PALLET_UID is null or
           remains_partion_in_otbor(rs.PRIHOD_PALLET_UID) <= 0 or
           (remains_partion_in_otbor(rs.PRIHOD_PALLET_UID) is null and remains_except_part_in_otb(rs.PRIHOD_PALLET_UID) > 0)
         );
    cursor rests_in_cell is
      select rm.remain, rm.uid_poleta, p.expiry_date, p.articul
        from rrl_remains rm join rrl_pallets p on rm.uid_poleta = p.uid_pallet
       where rm.cell = current_cell and rm.remain > 0 and p.articul = articul_for
       order by p.expiry_date;
  begin
    select condition, return_supplier_id into tmpVar, return_supplier_id1
      from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_ID1;
    if return_supplier_id1 is not null then
      return OTHOD_PALLET_PODBOR_PARTI4CELL(PALLET_ID1, 'RETURNS');
    end if;
    if tmpVar >= 2 then return -1; end if;
    for naklad_row in rowss loop
      count_of_PUID := 0;
      kolvo_otbora := naklad_row.quantity;
      articul_for := naklad_row.articul;
      select cell into current_cell from RRL_ARTICULS where ACTICUL = naklad_row.articul;
      for ddd8 in rests_in_cell loop
        exit when kolvo_otbora <= 0;
        count_of_PUID := count_of_PUID + 1;
        select PPP.MOD_ID into mod_id4 from RRL_PALLETS PPP where PPP.UID_PALLET = ddd8.UID_POLETA;
        update RRL_SBORKA_PALLET_ROWS
           set CURRENT_MOD_ID = mod_id4,
               PRIHOD_PALLET_UID = ddd8.UID_POLETA,
               PRIHOD_PALLET_UID_COUNT = count_of_PUID,
               EXPIRY_DATE = ddd8.EXPIRY_DATE
         where ID = naklad_row.ID;
        kolvo_otbora := 0;
      end loop;
    end loop;
    return 1;
  exception when no_data_found then return 0; end;
  function move_pall_2_picking_cell(pall_uid1 varchar2, user_id2 varchar2) return varchar2 is
    articul1 varchar2(50);
    cell1 varchar2(50);
    count1 number;
    tmp varchar2(50);
  begin
    begin
      select pts.articul, pts.unit_count into articul1, count1 from rrl_pallets pts where pts.uid_pallet = pall_uid1;
    exception when no_data_found then return 'no_pall'; end;
    select art.cell into cell1 from rrl_articuls art where art.acticul = articul1;
    tmp := RABAEV.RRL_INTERNAL_MOVE3(pallet_id => pall_uid1, cell_to => cell1, count1 => count1, user_id1 => user_id2);
    return tmp;
  exception when others then return 'error'; end;
  function close_othod_pall_row(PALLET_ROW_ID1 int, prih_pall_uid5 varchar2, kolvo_provod number, iser_id21 varchar2) return int is
  begin
    return 1;
  end;
  function get_remains_text(articul1 varchar2) return varchar2 is
  begin
    return ' [' || to_char(nvl(remains_free_all(articul1), 0)) || ']';
  end;
  function turnover_now(articul1 varchar2) return number is
    tmp number;
  begin
    select nvl(sum(rs.quantity), 0) into tmp
      from rrl_sborka_pallet_rows rs
      join rrl_sborka_pallets sp on rs.pallet_uid = sp.pallet_uid
     where rs.articul = articul1
       and nvl(sp.checking_time, sp.create_date) >= systimestamp - 30;
    return tmp;
  exception when others then return 0; end;
  function remains_of_prihods(articul1 varchar2, d_from date, d_to date) return number is
    tmp number;
  begin
    select nvl(sum(rm.remain), 0) into tmp
      from rrl_remains rm
      join rrl_pallets p on rm.uid_poleta = p.uid_pallet
     where p.articul = articul1
       and rm.remain > 0
       and nvl(p.creation_date, sysdate) >= d_from
       and nvl(p.creation_date, sysdate) < d_to;
    return tmp;
  exception when others then return 0; end;
  function storno_op(pall_uid1 varchar2, user_id1 varchar2) return int is
    tt_id1 int;
    tt_cond varchar2(255);
  begin
    begin
      select transtask_id into tt_id1 from rrl_sborka_pallets where pallet_uid = pall_uid1;
    exception when no_data_found then return -2; end;
    if tt_id1 is not null then
      begin
        select condition into tt_cond from rrl_transport_task where id = tt_id1;
        if tt_cond = '???????' then
          return -3;
        end if;
      exception when no_data_found then null; end;
    end if;
    update rrl_sborka_pallets
       set prooved = 0,
           prooved_by_scan = 0,
           checking_time = null,
           kladovshik = user_id1,
           trial_weight = null,
           wood_weight = null,
           count_of_errors = null,
           prim = null
     where pallet_uid = pall_uid1;
    return 1;
  end;
begin
  null;
end REMAINS;
/

prompt PACKAGE_BODY REVIZION

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."REVIZION" is

 
function revision_cond( rev_id int ) return int is
  ret int;
begin 
  select rr.condition into ret from rrl_revizion rr where id= rev_id;
  return ret;       
exception
         when no_data_found then return -1;
end;

 --- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int is
id1 int;    

  begin
      insert into RABAEV.RRL_REVIZION
      (
        WARE_ID     ,
        CREATE_DATE  ,
        CONDITION   ,
        USER_ID    
      )values (  ware_id1, sysdate  , 0 , user_id1  ) ;
      select RABAEV.RRL_REVISION_SQ.Currval into id1 from dual;

    return id1;
  end;

-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…
function clear_cell( cell1 varchar2 , puid varchar2   ) return int is  
begin

delete from rrl_remains rr where   rr.cell=cell1 and rr.uid_poleta= puid;
return  1;
exception
  when others then null;
end;

-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…
function clear_cell2( cell1 varchar2     ) return int is  
begin
delete from rrl_remains rr where   rr.cell=cell1  ;
return  1;
exception
  when others then null;
end;

-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor sss is 
       select  rm.cell , pts.articul 
       from rrl_remains rm , rrl_pallets pts where 
       rm.cell=cell1 and pts.uid_pallet=rm.uid_poleta
       group by rm.cell , pts.articul ;

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
  
  delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  and CELL= cell1;
  
  
  for s in sss loop
    
      insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , s.cell , sysdate , s.articul );
      select RRL_REVISION_ROW_SQ.Currval  into id1 from dual;

  end loop;


  return id1;
end;


-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
-- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… . 
   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;


-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 and pl.articul=articul2 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
-- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… . 
   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;



-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int is
   

revision_id1 int ;
row_ret int;
begin
  
    if(  revision_rowid > 0 ) then

          select rr.revision_id into revision_id1 from 
                 rrl_revision_row rr where id = revision_rowid;
    
          if revision_cond(revision_id1)>1 then
            return 0;
          end if;  
        -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
        -- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… . 
          update    RABAEV.RRL_REVISION_ROW rr set  rr.cell=cell1 , rr.articul1=articul2 
                    where id=revision_rowid ; 
          return revision_id1;
      else

      insert into RABAEV.RRL_REVISION_ROW  ( REVISION_ID , CELL , ARTICUL1      ) values 
           (rev_id2 , cell1 , articul2 );
           select RRL_REVISION_ROW_SQ.CURRVAL into row_ret from dual;
           return  row_ret;
      
    end if;
  
  --exception
  --  when no_data_found then return -1;
  --  when others then return -2;
  
end;




function articul_name( art varchar2 ) return varchar2 is
  ret varchar2(255);
  begin
    select name into ret from rrl_articuls where acticul=art;
    return ret;
    exception
      when no_data_found then return '';
      when others then return '';
  end;

function revision_cell_kor( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 is
rem5  varchar2(1024);
rem4  varchar2(255);
revision_row_id2 int;
condition2 int;
begin 

      begin  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ---  
         select rev.condition into condition2 from rrl_revizion rev where rev.id= revision_id1;
         if( condition2=2 ) then
             return 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…';
         end if;
         exception 
           when no_data_found then return 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…';
      end;  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… --- 
  
      begin  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ---      
           select id  into revision_row_id2 from RABAEV.RRL_REVISION_ROW where cell=cell1 and REVISION_ID = revision_id1  and rownum<=1 ;  
           exception 
             when no_data_found then revision_row_id2:=add_row_2_revizion(cell1 , revision_id1 ) ;
      end;  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… --- 
      
      
    rem4 := RABAEV.RRL_REVIZION_CELL_KOR( CELL1  ,    count2 ,    user_id3 )  ;
    
    rem5 :=concat( concat( ' РїС—Р…РїС—Р…РїС—Р…=' , to_char(count2) ) , concat( 'РїС—Р…РїС—Р…РїС—Р…. РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…=' , to_char( sysdate )  ));
    update RABAEV.RRL_REVISION_ROW set remark1= concat (remark1 , concat(rem5, rem4) )   , 
      count_kor=count2
     where id=revision_row_id2 ;
     return rem4;
      

end;



function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 is
rem5  varchar2(1026);
rem4  varchar2(255);
revision_row_id2 int;
condition2 int;
begin 

      begin  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ---  
         select rev.condition into condition2 from rrl_revizion rev where rev.id= revision_id1;
         if( condition2=2 ) then
             return 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…';
         end if;
         exception 
           when no_data_found then return 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…';
      end;  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… --- 
  
      begin  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ---      
           select id  into revision_row_id2 from RABAEV.RRL_REVISION_ROW where cell=cell1 and REVISION_ID = revision_id1  and rownum<=1 ;  
           exception 
             when no_data_found then revision_row_id2:=add_row_2_revizion(cell1 , revision_id1 ) ;
      end;  -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… --- 
      
      
    rem4 := RABAEV.RRL_REVIZION_CELL( CELL1  ,    count2 ,    user_id3 )  ;
    
    rem5 :=concat( concat( ' РїС—Р…РїС—Р…РїС—Р…=' , to_char(count2) ) , concat( 'sht. РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…=' , to_char( sysdate )  ));
    update RABAEV.RRL_REVISION_ROW set remark1= concat (remark1 , concat(rem5, rem4) )   , 
      count_kor=count2
     where id=revision_row_id2 ;
     return rem4;
      

end;


-- ============================================================================================

function  RRL_REVIZION_CELL_PALL( 
   articul1 varchar2, CELL1 varchar2 , count_pal int , revision_row_id1 int , 
    user_id1 varchar2 ) return varchar2

 -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…. РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…. 
-- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р….
--    РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…. 
is
new_event_uid int;
tmp varchar2 (250);
count_pal_fixed int;
counter_invent_p int;
/*cursor rema_in_p  is -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….
  select sum(rm.REMAIN) as RM1 , count( DISTINCT rm.UID_POLETA ) kk , 
  rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA
    and    pal.ARTICUL=articul1  and rm.REMAIN>0
  order by    pal.EXPIRY_DATE asc; */

-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….
rows_cnt int;
cursor rema is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

cursor rema_invent_p  is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

begin
count_pal_fixed:=0;
rows_cnt:=0;

-- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
for rrow in rema loop
  rows_cnt:=rows_cnt+1;
    count_pal_fixed:=count_pal_fixed+1;
    if(count_pal_fixed>count_pal) then -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…
        tmp := RABAEV.RRL_INTERNAL_MOVE2(
            rrow.UID_POLETA ,  'INVENT_P' ,
            rrow.remain , user_id1 );
     end if;
end loop;

if( count_pal_fixed>count_pal  ) then
tmp:= concat( 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ' , concat( to_char( count_pal_fixed-count_pal ) , ' РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…'));
end if;

if( count_pal_fixed < count_pal  ) then
tmp:= concat( 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ' , concat( to_char(count_pal- count_pal_fixed ) , ' РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…'));
counter_invent_p:=0;
      for rrow2 in rema_invent_p loop -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….
          counter_invent_p:=counter_invent_p+1;    
          if(  counter_invent_p<=count_pal-count_pal_fixed ) then
          
           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid, 'INVENT_P' , CELL1 , systimestamp , 
           rrow2.remain ,2 ,rrow2.uid_poleta, user_id1 );
          
          end if;
      end loop;
end if;

if( count_pal_fixed = count_pal  ) then
 tmp:= 'ok';
end if;
 
update RRL_REVISION_ROW set REMARK1 = tmp , NUM_OF_PALL=count_pal  where id=revision_row_id1;
commit;
return tmp;

exception 
       when no_data_found then  return 'neok';
       when others then raise;


END;


-- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….
function  RRL_REVIZION_CLEAR_MINUS( revision_id1 int , user_id1 varchar2 ) return int is
 new_event_uid int;
 cell4 varchar2(255);
 tmp varchar2(255);
 articul5 varchar2(255);
 
 cursor cells1  is select distinct rr.cell , rr.articul1 from rrl_revision_row rr 
 where rr.revision_id=revision_id1 ;

 cursor min_rem is select rem1.cell , rem1.uid_poleta , rem1.remain 
        from rrl_remains rem1 , rrl_pallets pts where pts.uid_pallet=rem1.uid_poleta and
        pts.articul = articul5 and  rem1.cell=cell4 and rem1.remain<0;

begin

    for cell3 in cells1 loop
    cell4:=cell3.cell;    
    articul5:=cell3.articul1;
        for rrow in min_rem loop   
           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid , CELL4 , 'INVENT_P'  , systimestamp , 
           rrow.remain ,2 ,rrow.uid_poleta, user_id1 );
        end loop;
        
    end loop;
    commit;
return 1;
end;

function  RRL_REVIZION_CELL_SHT( 
   articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , 
    user_id1 varchar2 ) return varchar2

 -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…. РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…. 
-- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р….
--    РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…. 
is
new_event_uid int;
tmp varchar2 (250);
counter_invent_p number;
to_spis number;

-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….

cursor rema is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

cursor rema_invent_p  is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

count_sht_rem number;
how_many_return number;

begin


count_sht_rem:= 0;
to_spis:=0;

-- РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… 
for rrow in rema loop
--   РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…  РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…, РїС—Р…РїС—Р… 
--        РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…, РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…= РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…
--        РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… := 0
     count_sht_rem:=count_sht_rem+rrow.remain;
    if( count_sht_rem>count_sht ) then
        if( count_sht_rem-count_sht>rrow.remain ) then
                   tmp := RABAEV.RRL_INTERNAL_MOVE2(
                      rrow.UID_POLETA ,  'INVENT_P' ,
                      rrow.remain , user_id1 );
            else
                   tmp := RABAEV.RRL_INTERNAL_MOVE2(
                      rrow.UID_POLETA ,  'INVENT_P' ,
                      count_sht_rem-count_sht , user_id1 );
        end if;
    end if;
   
              
end loop;


if( count_sht_rem=count_sht  ) then
    tmp:= 'ok';
end if;


if( count_sht_rem-count_sht>0  ) then
tmp:= concat( 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ' , concat( to_char( count_sht_rem-count_sht ) , ' РїС—Р…РїС—Р…'));
end if;

if( count_sht_rem-count_sht<0  ) then
tmp:= concat( 'РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… ' , concat( to_char( -count_sht_rem+count_sht ) , ' РїС—Р…РїС—Р…'));
counter_invent_p:=0;
how_many_return:=-count_sht_rem+count_sht;

      for rrow2 in rema_invent_p loop -- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….
          counter_invent_p:=counter_invent_p+rrow2.remain;
          if( how_many_return>0 ) then        
              if( rrow2.remain>how_many_return ) then
                  to_spis:=how_many_return;
                  how_many_return:=0;
              else
                  to_spis:=rrow2.remain;
                  how_many_return:=how_many_return-rrow2.remain;
              end if;

           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid, 'INVENT_P' , CELL1 , systimestamp , 
          /* rrow2.remain */ to_spis ,2 ,rrow2.uid_poleta, user_id1 );

          end if;
      end loop;
      
end if;


 
update RRL_REVISION_ROW set REMARK1 = tmp , count1=count_sht  where id=revision_row_id1;
commit;
return tmp;

exception 
       when no_data_found then  return 'neok';
       when others then raise;


END;



function CreateNaklad_2_revizion( rev_id1 int ) return int is
         rev_naklad_id1 int;
         ret int;
         ware_id3 int;
begin

  select r.rev_naklad_id , ware_id into rev_naklad_id1 , ware_id3 from rrl_revizion r where id= rev_id1;
  if( not rev_naklad_id1 is null ) and (  rev_naklad_id1 >0 ) then
      return rev_naklad_id1;
  end if;

  ret:=ADD_RRL_PRIH_NAKLAD2( NAKLAD_NUMBER => concat( 'INV_' , to_char(rev_id1) ) , 
                         DATE_OF_NAKLAD => sysdate ,DATE_OF_ACCEPT => sysdate,
                         POSTAVSHIK_NAME => 'INV', 
                         SM_NAKLAD_NUMBER => concat( 'INV_' , to_char(rev_id1) ) ,
                         ZAKAZ_NUMBER1 => concat( 'INV_' , to_char(rev_id1) ) ,
                         ware_id1 => ware_id3 );
               
  if( ret>0 ) then
      update RABAEV.RRL_PRIHOD_NAKLAD set condition=2 where id=ret;
      update  rrl_revizion set rev_naklad_id=ret where id= rev_id1;
  end if;
            
  return ret;
exception
  when no_data_found then return -1;
  when others then return -2;
end;

-- ============================================================================================


FUNCTION  RRL_INV_CREATE_LINE5 
( 
    cell1 varchar2 ,
    articul2 varchar2,
    count1 NUMBER ,
    expiury_date date ,
    fasovka_id1 int ,
    brak_perc1 number ,
    pall_weight1 number , 
    pall_n int ,
    tn_weight1 number ,
    count_kor1 number ,
    user_id2 varchar2 , 
    NAKLAD_ID int
)
    RETURN varchar2 IS 
    price Number;
    ret2 varchar2(255);
    event_id int;
    pallet_name varchar2(255);


BEGIN
-- =================================================
pallet_name:= CONCAT( Concat( Concat( Concat('P_' , articul2 ) , '_G3_') , cell1) , concat( '_' ,to_char(pall_n) ) ) ;
pallet_name:=replace(pallet_name , 'РїС—Р…' ,'T' );
begin
        insert into RABAEV.RRL_PALLETS
        (
          UID_PALLET       ,
          ARTICUL           ,
          CREATION_DATE     ,
          EXPIRY_DATE       ,
          UNIT_COUNT        ,
          PRICE             ,
          PRIHOD_NAKLAD_ID  
        )values
        (
            pallet_name , 
            articul2 ,
            sysdate ,
            expiury_date ,
            count1 , 
            1,
            NAKLAD_ID
        );
        exception
          when others then return 'EXISTS';
end;
-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…

 select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
 event_id:=event_id+1;
        
insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          CELL1 ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          user_id2 ,
          NAKLAD_ID 
            );
    
    ret2:=RABAEV.RRL_PRIHODPALLET_CHANGE(PALLET_UID1 => pallet_name ,art => articul2 ,
        UNIT_COUNT1 => count1 ,DEFECT_PERC1 => brak_perc1 ,COUNT_KOR1 => count_kor1 ,
        WEIGHT_BRUTTO1 => pall_weight1 , WEIGHT_TN1 => tn_weight1 ,MOD_ID1 => fasovka_id1 );

return pallet_name;
-- =================================================
END ;



FUNCTION  close_revision( rev_id int ) return int is
  tmp int;
begin
  
  tmp:= REVIZION.rev_create_snap_shot_after( rev_id );
  update rrl_revizion rev set rev.condition=2 where rev.id=rev_id;
  
  return 1;
end;


-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…
-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….
function rev_create_snap_shot_before( rev_id int ) return int is
    snap_id1 int;
    tmp int;
    cursor sss is select rs.cell , rs.articul1  
     from rrl_revision_row rs where rs.revision_id = rev_id ;
begin
 
  select rv.SNAPSHOT_BEFORE into snap_id1 
         from rrl_revizion rv where id= rev_id;
  if( snap_id1 is null ) then
  update rrl_revizion set condition=1 where ID= rev_id;
  
      snap_id1 := REMAINS.create_snapshot(type2 => 1);
      update rrl_revizion set SNAPSHOT_BEFORE=snap_id1 where  id= rev_id;
      for s in sss loop
          tmp:=REMAINS.add_row_2_snapshot(snap_shot_id1 => snap_id1 ,cell1 => s.cell ,articul1 => s.articul1);
      end loop;
      
      return snap_id1;
  else
      return snap_id1;
  end if;
return snap_id1;
end;
-- РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р… РїС—Р…РїС—Р… РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р…РїС—Р….


function rev_create_snap_shot_after( rev_id int ) return int is
    snap_id1 int;
    tmp int;
    cursor sss is select rs.cell , rs.articul1  
     from rrl_revision_row rs where rs.revision_id = rev_id ;
begin
 
  select rv.SNAPSHOT_AFTER into snap_id1 
         from rrl_revizion rv where id= rev_id;
  if( snap_id1 is null ) then
      snap_id1 := REMAINS.create_snapshot(type2 => 2);
      update rrl_revizion set SNAPSHOT_AFTER=snap_id1 where  id= rev_id;
      for s in sss loop
          tmp:=REMAINS.add_row_2_snapshot(snap_shot_id1 => snap_id1 ,cell1 => s.cell ,articul1 => s.articul1);
      end loop;
      
      return snap_id1;
  else
      return snap_id1;
  end if;
return snap_id1;
end;


function remain_before( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number is
 snap_before int;
 snap_after int;
ret number;
begin

    select rr.snapshot_before , rr.snapshot_after 
    into snap_before ,  snap_after
     from rrl_revizion rr 
    where rr.id=rev_id;
    
    
  select sum(rsr.remain) into ret from rrl_remain_snapshot_rows rsr where rsr.snap_shot_id = snap_before and 
  rsr.articul = articul1 and rsr.cell=cell1 ;
return ret;
exception     
       when no_data_found then return null;
       when others then return -9999;
end;


function remain_after( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number is
 snap_before int;
 snap_after int;
ret number;
begin

    select rr.snapshot_before , rr.snapshot_after 
    into snap_before ,  snap_after
     from rrl_revizion rr 
    where rr.id=rev_id;

  select sum(rsr.remain) into ret from rrl_remain_snapshot_rows rsr where rsr.snap_shot_id = snap_after and 
  rsr.articul = articul1 and rsr.cell=cell1 ;
return ret;
exception     
       when no_data_found then return null;
       when others then return -9999;
end;



begin
null;
end REVIZION;
/

prompt PACKAGE_BODY TRANSPORT_TASK

  CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."TRANSPORT_TASK" is

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
    return to_char(count_kor1) || ' Р С”Р С•РЎР‚.';
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
    if articul1 = 'Р Тђ0000012233' then
      return to_char(count_kor1) || ' Р С”Р С•РЎР‚.';
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
    return 'Р СњР ВµР Т‘Р С•РЎРѓРЎвЂљР В°РЎвЂљР С•РЎвЂЎР Р…Р В°РЎРЏ Р В·Р В°Р С–РЎР‚РЎС“Р В·Р С”Р В° Р СР В°РЎР‚РЎв‚¬РЎР‚РЎС“РЎвЂљР В°: ' || to_char(cnt_pt) || ' < ' || to_char(ml);
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

