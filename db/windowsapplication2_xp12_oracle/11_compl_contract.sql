prompt [11] COMPL compatibility package

create or replace package COMPL is
  function update_seq(articul1 varchar2, ware_id1 int, SQ1 int, SQGROUP int) return int;
  function show_sq(articul1 varchar2, ware_id1 int) return int;
  function show_sq_gr(articul1 varchar2, ware_id1 int) return int;
  function divide_st_bypal(stn varchar2, ware_id1 int) return int;
  function create_order_from_spallets(st_numb varchar2, user_id1 varchar2) return int;
  function path(articul1 varchar2, sborka_pallet_uid varchar2) return varchar2;
  function truncate_order_by_remains(ware_id6 int) return int;
  function orders_start_plan(ord_id1 int) return int;
  function orders_create_vycherk(ord_id1 int) return int;
  function orders_check(ware_id6 int) return int;
  function order_rows_count(order_id1 int) return int;
  function order_vycherk_count(order_id1 int) return int;
  function reset_2_first_status(order_id1 int) return int;
  function debug_truncate_rem(articul1 varchar2, ware_id6 int) return number;
  function debug_truncate_reserv(articul1 varchar2, ware_id6 int) return number;
  function debug_truncate_orders(articul1 varchar2, ware_id6 int) return number;
  function RRL_GIVE_PALLET_UID(ST_NUMBER1 varchar2, USER_ID1 varchar2, PALLET_NUMBER1 int) return varchar2;
  function RRL_SBORKA_PAL_REMOVE_EMPTY(ST_NUMBER1 varchar2, USER_ID1 varchar2) return int;
  function RRL_COPY_PALLET_ROW3(row_id2 int, count1 number, PALLET_UID_NEW VARCHAR2) return int;
  function SET_SBORSHIK(PALLET_UID1 varchar2, SBORSHIK1 varchar2, user_id1 varchar2) return int;
  function pallet_compl_date(pall_uid varchar2) return date;
  function time_shift_start(time1 date) return date;
  function time_shift_end(time1 date) return date;
end COMPL;
/

create or replace package body COMPL is
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
