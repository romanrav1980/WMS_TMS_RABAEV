package PRIHOD is
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
