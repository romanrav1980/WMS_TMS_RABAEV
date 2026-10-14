package body PRIHOD is
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
