package body TRANSPORT_PLN is
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
