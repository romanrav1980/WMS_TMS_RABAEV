prompt [12] ORDERS compatibility package

create or replace package ORDERS is
  function cleanup_order(ord_id int) return int;
  function DELETE_PALLETS(ST_NUMBER1 varchar2, user_id1 varchar2) return varchar2;
  function create_order(
    st_numb1 varchar2,
    CREATE_DATE1 date,
    WARE_ID1 integer,
    ADDR1 varchar2,
    STATE1 varchar2,
    ORDDATE1 date,
    user_id1 varchar2
  ) return int;
  function add_order_row(ord_id int, ARTICUL1 varchar2, QUANTITY1 number, WARE_ID1 int) return int;
  function cleanup_order2(ord_number1 varchar2) return int;
  function contains_invalid_logo(ord_number1 varchar2) return int;
  function wares_of_order(ord_number1 varchar2) return varchar2;
  function count_of_sq_gr(ord_number1 varchar2) return int;
  function get_unfinished_quantity(articul1 varchar2, from_date1 date) return number;
  function get_unfinished_quantityo(articul1 varchar2, from_date1 date) return number;
end ORDERS;
/

create or replace package body ORDERS is
  function ei_by_type_w(type_w int) return varchar2 is
  begin
    if type_w in (0, 7) then return 'РЎв‚¬РЎвЂљ';
    elsif type_w in (8, 1, 6, 5, 2, 3) then return 'Р С”Р С–';
    else return 'РЎв‚¬РЎвЂљ'; end if;
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
           art.name, case when art.type_w in (0, 7) then 'шт' when art.type_w in (8, 1, 6, 5, 2, 3) then 'кг' else 'шт' end
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
